"""Stage 8 (printer handoff) — fully OFFLINE unit tests.

Pure payload/path builders are pinned to blueprint/printer-control-cheatsheet.md;
network actions are only exercised on UNCONFIGURED configs (must guard, not crash)
or against 127.0.0.1 where nothing listens (instant local refusal, no real network).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agent import pipeline, printer
from agent.config import Config, printer_configured


def make_cfg(**kw) -> Config:
    """Config without load_config(): no .env, no slicer detection, no network."""
    return Config(slicer_bin=Path("/nonexistent/slicer"), **kw)


# --------------------------------------------------------------------------- #
# PURE builders
# --------------------------------------------------------------------------- #


def test_mqtt_topics():
    assert printer.mqtt_topics("01ABC") == ("device/01ABC/request", "device/01ABC/report")


def test_project_file_payload_matches_cheatsheet():
    # EXACT shape from blueprint/printer-control-cheatsheet.md
    assert printer.build_project_file_payload() == {
        "print": {
            "command": "project_file",
            "param": "Metadata/plate_1.gcode",
            "url": "file:///mnt/sdcard",
            "subtask_name": "job",
            "bed_type": "auto",
            "bed_levelling": True,
            "flow_cali": True,
            "use_ams": False,
        }
    }


def test_project_file_payload_overrides():
    p = printer.build_project_file_payload(
        gcode_path="Metadata/plate_2.gcode",
        subtask_name="gear20_x6",
        url="ftp:///gear20_x6.gcode.3mf",
        use_ams=True,
    )["print"]
    assert p["param"] == "Metadata/plate_2.gcode"
    assert p["subtask_name"] == "gear20_x6"
    assert p["url"] == "ftp:///gear20_x6.gcode.3mf"
    assert p["use_ams"] is True
    assert p["bed_levelling"] is True and p["flow_cali"] is True  # never dropped


def test_pushall_payload():
    assert printer.build_pushall_payload() == {
        "pushing": {"command": "pushall", "version": 1, "push_target": 1}
    }


@pytest.mark.parametrize(
    ("builder", "command"),
    [
        (printer.build_stop_payload, "stop"),
        (printer.build_pause_payload, "pause"),
        (printer.build_resume_payload, "resume"),
    ],
)
def test_stop_pause_resume_payloads(builder, command):
    assert builder() == {"print": {"command": command, "param": ""}}


def test_gcode_line_payload():
    assert printer.build_gcode_line_payload("G28") == {
        "print": {"command": "gcode_line", "param": "G28"}
    }


def test_remote_ftp_path():
    got = printer.remote_ftp_path(Path("output/gear_x6/gear20_x6.gcode.3mf"))
    assert got == "/gear20_x6.gcode.3mf"  # SD-card root, basename only
    assert printer.remote_ftp_path(Path("job.gcode.3mf")) == "/job.gcode.3mf"


# --------------------------------------------------------------------------- #
# Config helper
# --------------------------------------------------------------------------- #


def test_printer_configured():
    assert not printer_configured(make_cfg())
    assert not printer_configured(make_cfg(a1_ip="192.168.1.50", a1_serial="01ABC"))
    assert printer_configured(
        make_cfg(a1_ip="192.168.1.50", a1_serial="01ABC", a1_access_code="12345678")
    )


# --------------------------------------------------------------------------- #
# GUARDED network actions — unconfigured/unreachable must not crash the pipeline
# --------------------------------------------------------------------------- #


def test_ping_unconfigured_returns_false():
    assert printer.ping(make_cfg()) is False  # no raise, no network


def test_ping_unreachable_returns_false():
    # 127.0.0.1:8883 with no broker -> instant local refusal (still offline-safe).
    cfg = make_cfg(a1_ip="127.0.0.1", a1_serial="01ABC", a1_access_code="12345678")
    assert printer.ping(cfg) is False


@pytest.mark.parametrize(
    "action",
    [
        lambda cfg: printer.upload(cfg, Path("whatever.gcode.3mf")),
        lambda cfg: printer.start_print(cfg, "/whatever.gcode.3mf"),
        lambda cfg: printer.handoff(cfg, Path("whatever.gcode.3mf")),
    ],
)
def test_actions_unconfigured_raise_printer_unavailable(action):
    with pytest.raises(printer.PrinterUnavailable, match="not configured"):
        action(make_cfg())


def test_upload_missing_file():
    cfg = make_cfg(a1_ip="127.0.0.1", a1_serial="01ABC", a1_access_code="12345678")
    with pytest.raises(FileNotFoundError):
        printer.upload(cfg, Path("/no/such/file.gcode.3mf"))


# --------------------------------------------------------------------------- #
# CLI seams (BRAIN step 0 `ping` / step 7 `send`) — unconfigured => exit 0
# --------------------------------------------------------------------------- #


def test_cli_ping_unconfigured_exits_zero(monkeypatch, capsys):
    monkeypatch.setattr(pipeline, "load_config", make_cfg)
    with pytest.raises(SystemExit) as exc:
        pipeline.main(["ping"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "not configured" in out and "A1_IP" in out


def test_cli_send_unconfigured_prints_hint_and_exits_zero(monkeypatch, capsys):
    monkeypatch.setattr(pipeline, "load_config", make_cfg)
    pipeline.main(["send", "output/gear/gear20_x1.gcode.3mf"])  # returns, no SystemExit
    out = capsys.readouterr().out
    assert "not configured" in out
    assert "A1_IP" in out and "A1_SERIAL" in out and "A1_ACCESS_CODE" in out
