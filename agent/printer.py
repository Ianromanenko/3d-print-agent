"""Stage 8: printer handoff — FTPS upload + MQTT print start on a Bambu Lab A1.

Implements `blueprint/printer-control-cheatsheet.md` exactly:
- MQTT:  mqtts://<A1_IP>:8883, TLS with a self-signed cert (verification OFF),
  user `bblp`, password = LAN Access Code. Publish to `device/<serial>/request`,
  subscribe to `device/<serial>/report`.
- FTP:   implicit FTPS on port 990 (same user/password); the sliced `.gcode.3mf`
  lands in the SD-card root, then MQTT `project_file` starts it without re-slicing.

The module is split into PURE payload/path builders (unit-testable, zero network)
and GUARDED network actions (never touch the network when unconfigured; `ping`
never raises). Transport: `bambulabs-api` when importable (preferred, field-proven
implicit-FTPS + MQTT client), raw `paho-mqtt` + `ftplib` fallback otherwise.

NOTE: written and unit-tested offline — end-to-end against a live A1 is stage 9.
"""

from __future__ import annotations

import json
import socket
import ssl
import time
from ftplib import FTP_TLS
from pathlib import Path, PurePosixPath

from agent.config import Config, printer_configured

MQTT_PORT = 8883
MQTT_USER = "bblp"
FTPS_PORT = 990
FTPS_USER = "bblp"
PING_TIMEOUT_S = 3.0
NET_TIMEOUT_S = 20.0
# Inside a Studio/Orca `.gcode.3mf` the sliced plate always sits here (single plate).
GCODE_IN_3MF = "Metadata/plate_1.gcode"

try:  # preferred transport (installs cleanly on 3.12/arm64)
    import bambulabs_api as _bbl

    HAVE_BAMBULABS_API = True
except ImportError:  # pragma: no cover - depends on the environment
    _bbl = None
    HAVE_BAMBULABS_API = False


class PrinterUnavailable(RuntimeError):
    """Printer is not configured or cannot be reached — caller decides how soft to fail."""


# --------------------------------------------------------------------------- #
# PURE builders (no network; these are what the unit tests pin down)
# --------------------------------------------------------------------------- #


def mqtt_topics(serial: str) -> tuple[str, str]:
    """(request_topic, report_topic) for a printer serial."""
    return (f"device/{serial}/request", f"device/{serial}/report")


def build_project_file_payload(
    gcode_path: str = "Metadata/plate_1.gcode",
    subtask_name: str = "job",
    url: str = "file:///mnt/sdcard",
    use_ams: bool = False,
) -> dict:
    """`project_file` command: start an already-sliced 3MF sitting on the device.

    Exact shape from the cheatsheet. `url` may also be `ftp:///<file>.3mf` for a
    file just uploaded over FTPS (see `remote_ftp_path`).
    """
    return {
        "print": {
            "command": "project_file",
            "param": gcode_path,
            "url": url,
            "subtask_name": subtask_name,
            "bed_type": "auto",
            "bed_levelling": True,
            "flow_cali": True,
            "use_ams": use_ams,
        }
    }


def build_pushall_payload() -> dict:
    """Request a full status push on the report topic."""
    return {"pushing": {"command": "pushall", "version": 1, "push_target": 1}}


def _print_command(command: str, param: str = "") -> dict:
    return {"print": {"command": command, "param": param}}


def build_stop_payload() -> dict:
    return _print_command("stop")


def build_pause_payload() -> dict:
    return _print_command("pause")


def build_resume_payload() -> dict:
    return _print_command("resume")


def build_gcode_line_payload(line: str) -> dict:
    """Inline g-code execution (e.g. `G28`, LED macros)."""
    return _print_command("gcode_line", line)


def remote_ftp_path(gcode_3mf: Path) -> str:
    """Device path where `upload` puts the file: SD-card root, same basename."""
    return "/" + Path(gcode_3mf).name


# --------------------------------------------------------------------------- #
# Implicit FTPS (port 990). Stock ftplib.FTP_TLS only does *explicit* FTPS
# (AUTH TLS after plain connect); the A1 wants the socket TLS-wrapped from the
# first byte. Standard recipe: wrap the socket as soon as connect() assigns it.
# --------------------------------------------------------------------------- #


class ImplicitFTP_TLS(FTP_TLS):
    """ftplib.FTP_TLS subclass speaking *implicit* FTPS (TLS from connect)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sock: socket.socket | None = None

    @property
    def sock(self):
        return self._sock

    @sock.setter
    def sock(self, value):
        """TLS-wrap the plain socket the moment FTP.connect() sets it."""
        if value is not None and not isinstance(value, ssl.SSLSocket):
            value = self.context.wrap_socket(value)
        self._sock = value


def _insecure_tls_context() -> ssl.SSLContext:
    """TLS context for the A1's self-signed certificate (no verification)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


# --------------------------------------------------------------------------- #
# GUARDED network actions
# --------------------------------------------------------------------------- #


def _require_configured(cfg: Config) -> None:
    if not printer_configured(cfg):
        raise PrinterUnavailable(
            "printer not configured: fill A1_IP / A1_SERIAL / A1_ACCESS_CODE in .env "
            "(A1 must be in LAN Mode + Developer Mode)"
        )


def ping(cfg: Config) -> bool:
    """Is the A1 reachable? TCP connect to <ip>:8883. NEVER raises.

    False when unconfigured or unreachable — BRAIN step 0 warns but does not block.
    """
    if not printer_configured(cfg):
        return False
    try:
        with socket.create_connection((cfg.a1_ip, MQTT_PORT), timeout=PING_TIMEOUT_S):
            return True
    except OSError:
        return False


def upload(cfg: Config, gcode_3mf: Path) -> str:
    """Upload the sliced `.gcode.3mf` over implicit FTPS; return the device path."""
    _require_configured(cfg)
    gcode_3mf = Path(gcode_3mf)
    if not gcode_3mf.is_file():
        raise FileNotFoundError(f"no such file to upload: {gcode_3mf}")
    device_path = remote_ftp_path(gcode_3mf)
    try:
        if HAVE_BAMBULABS_API:
            printer = _bbl.Printer(cfg.a1_ip, cfg.a1_access_code, cfg.a1_serial)
            with open(gcode_3mf, "rb") as fh:
                res = printer.upload_file(fh, gcode_3mf.name)
            # bambulabs-api returns the STOR response ("226 Transfer complete")
            # on success and swallows transfer errors into None/"No file uploaded."
            if not res or "226" not in str(res):
                raise PrinterUnavailable(f"FTPS upload rejected by printer: {res!r}")
        else:
            ftps = ImplicitFTP_TLS(context=_insecure_tls_context(), timeout=NET_TIMEOUT_S)
            ftps.connect(host=cfg.a1_ip, port=FTPS_PORT)
            ftps.login(user=FTPS_USER, passwd=cfg.a1_access_code)
            ftps.prot_p()  # encrypt the data channel too
            try:
                with open(gcode_3mf, "rb") as fh:
                    ftps.storbinary(f"STOR {gcode_3mf.name}", fh, blocksize=32768)
            finally:
                ftps.close()
    except PrinterUnavailable:
        raise
    except Exception as e:  # network/auth/TLS — one clear failure type for callers
        raise PrinterUnavailable(
            f"FTPS upload to {cfg.a1_ip}:{FTPS_PORT} failed: {e}"
        ) from e
    return device_path


def start_print(cfg: Config, device_path: str) -> None:
    """Publish `project_file` for an uploaded 3MF (job shows up in Bambu Handy)."""
    _require_configured(cfg)
    filename = PurePosixPath(device_path).name
    try:
        if HAVE_BAMBULABS_API:
            _start_print_bbl(cfg, filename)
        else:
            payload = build_project_file_payload(
                gcode_path=GCODE_IN_3MF,
                subtask_name=PurePosixPath(filename).stem,
                url=f"ftp://{device_path}",  # "/f.gcode.3mf" -> "ftp:///f.gcode.3mf"
            )
            _publish_paho(cfg, payload)
    except PrinterUnavailable:
        raise
    except Exception as e:
        raise PrinterUnavailable(
            f"MQTT start_print via {cfg.a1_ip}:{MQTT_PORT} failed: {e}"
        ) from e


def _start_print_bbl(cfg: Config, filename: str) -> None:
    """bambulabs-api path: MQTT-only connect (skip Printer.connect() — it also
    starts the camera stream), wait for the session, fire project_file."""
    mc = _bbl.Printer(cfg.a1_ip, cfg.a1_access_code, cfg.a1_serial).mqtt_client
    mc.connect()
    mc.start()
    try:
        deadline = time.monotonic() + NET_TIMEOUT_S
        while not mc.is_connected():
            if time.monotonic() > deadline:
                raise PrinterUnavailable(
                    f"MQTT connect to {cfg.a1_ip}:{MQTT_PORT} timed out "
                    f"({NET_TIMEOUT_S:.0f}s) — A1 off / wrong access code?"
                )
            time.sleep(0.2)
        ok = mc.start_print_3mf(filename, GCODE_IN_3MF, use_ams=False)
        if not ok:
            raise PrinterUnavailable(f"printer rejected project_file for {filename!r}")
    finally:
        mc.stop()


def _publish_paho(cfg: Config, payload: dict) -> None:
    """Raw fallback: one QoS-1 publish to device/<serial>/request over TLS 8883."""
    import paho.mqtt.client as mqtt

    request_topic, _ = mqtt_topics(cfg.a1_serial)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311)
    client.username_pw_set(MQTT_USER, cfg.a1_access_code)
    client.tls_set(cert_reqs=ssl.CERT_NONE)  # self-signed printer cert
    client.tls_insecure_set(True)
    client.connect(cfg.a1_ip, MQTT_PORT, keepalive=30)
    client.loop_start()
    try:
        info = client.publish(request_topic, json.dumps(payload), qos=1)
        info.wait_for_publish(timeout=NET_TIMEOUT_S)
        if not info.is_published():
            raise PrinterUnavailable(f"publish to {request_topic} not acknowledged")
    finally:
        client.loop_stop()
        client.disconnect()


def handoff(cfg: Config, gcode_3mf: Path) -> None:
    """Stage-7 -> stage-8 seam: FTPS upload, then MQTT project_file start."""
    device_path = upload(cfg, gcode_3mf)
    start_print(cfg, device_path)
