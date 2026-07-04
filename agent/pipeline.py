"""Pipeline orchestrator + CLI (the deterministic tool the BRAIN.md session calls).

Usage (inside the uv venv):
    python -m agent.pipeline parse "<запрос>"    # heuristic BuildSpec JSON draft -> stdout
    python -m agent.pipeline spec  <spec.json>   # confirmed spec -> generate/gate/slice
    python -m agent.pipeline verify <spec.json>  # generate/gate/render -> rubric JSON (NO slice)
    python -m agent.pipeline run   "<запрос>"    # parse -> clarify gate -> build
    python -m agent.pipeline gear [--count N]    # demo: 1..N Ø20 spur gears end-to-end
    python -m agent.pipeline ping                # printer reachability (stage 8; exit 0 either way)
    python -m agent.pipeline send <f.gcode.3mf>  # FTPS upload + MQTT start on the A1 (stage 8)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent.clarify import confirm_interactive, open_questions, restate
from agent.config import load_config, printer_configured
from agent.generate.cad import generate_object
from agent.intake import parse_request
from agent.printability import check_and_repair
from agent.slice import slice_objects
from agent.spec import BuildSpec, ObjectSpec, spec_from_json, spec_to_json


def run_spec(spec: BuildSpec, out_dir: Path) -> Path:
    """Shared deterministic core: generate -> printability gate -> slice.

    Routes each object by kind (mechanical -> code-CAD; organic -> stage 4b,
    not built yet), gates every STL, then slices all gated STLs together
    (arrange=True -> N separate objects on one plate)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== 1/3 CAD generate: {spec.source_request}")
    stls: list[Path] = []
    for obj in spec.objects:
        if obj.kind == "organic":
            raise NotImplementedError("organic/mesh generation is stage 4b — not built yet")
        paths = generate_object(obj, out_dir)
        for p in paths:
            print(f"  generated {p} ({p.stat().st_size} bytes)")
        stls.extend(paths)

    print("=== 2/3 printability gate")
    gated: list[Path] = []
    for stl in stls:
        res = check_and_repair(stl, out_dir / "gate")
        print("  " + res.report.replace("\n", "\n  "))
        if not res.ok:
            print(f"FATAL: {stl.name} failed the printability gate", file=sys.stderr)
            sys.exit(2)
        gated.extend(res.output_paths)

    print(f"=== 3/3 slice ({len(gated)} object(s), arrange=True, PETG HF)")
    total = sum(o.count for o in spec.objects)
    out = out_dir / f"{spec.objects[0].name}_x{total}.gcode.3mf"
    result = slice_objects(gated, out, arrange=True)
    print(f"DONE: {result} ({result.stat().st_size} bytes)")
    return result


def _spec_out_dir(spec: BuildSpec) -> Path:
    cfg = load_config()
    total = sum(o.count for o in spec.objects)
    name = spec.objects[0].name if spec.objects else "build"
    return cfg.output_dir / (name if total == 1 else f"{name}_x{total}")


def run_gear(count: int = 1) -> Path:
    cfg = load_config()
    spec = BuildSpec(
        objects=[
            ObjectSpec(
                name="gear20",
                kind="mechanical",
                # Ø20 outer with 20 teeth -> module = 20/22 ~ 0.909 (pitch Ø ~18.18)
                dims_mm={"outer_d": 20.0, "teeth": 20, "thickness": 5.0, "bore": 5.0},
                count=count,
            )
        ],
        source_request=f"{count}x spur gear Ø20mm, 5mm thick, 5mm bore",
    )
    out_dir = cfg.output_dir / ("gear" if count == 1 else f"gear_x{count}")
    return run_spec(spec, out_dir)


def run_verify(spec_file: Path) -> list[dict]:
    """`verify` subcommand (BRAIN.md step 5, BEFORE slicing): generate -> gate ->
    render + measure -> print a JSON list of rubrics on stdout.

    Deterministic slots (proportions/mechanical/printability) are filled;
    visual slots (geometry/features) are null — the brain looks at the render
    PNGs and fills them, releasing only at >= 95%. Progress goes to stderr so
    stdout stays pure JSON."""
    from agent.verify import verify_object  # lazy: pulls in pyvista/VTK

    spec = spec_from_json(Path(spec_file).read_text(encoding="utf-8"))
    out_dir = _spec_out_dir(spec) / "verify"
    out_dir.mkdir(parents=True, exist_ok=True)

    rubrics: list[dict] = []
    for obj in spec.objects:
        if obj.kind == "organic":
            raise NotImplementedError("organic/mesh generation is stage 4b — not built yet")
        print(f"=== verify {obj.name}: generate", file=sys.stderr)
        for stl in generate_object(obj, out_dir):
            res = check_and_repair(stl, out_dir / "gate")
            print("  " + res.report.replace("\n", "\n  "), file=sys.stderr)
            for gated in res.output_paths:
                print(f"  render+measure {gated.name}", file=sys.stderr)
                rubrics.append(verify_object(obj, gated, out_dir / "renders", res.ok))
    print(json.dumps(rubrics, indent=2, ensure_ascii=False))
    return rubrics


def run_from_file(spec_file: Path) -> Path:
    """`spec` subcommand: confirmed spec.json -> build (the brain calls this AFTER clarify)."""
    spec = spec_from_json(Path(spec_file).read_text(encoding="utf-8"))
    return run_spec(spec, _spec_out_dir(spec))


def run_request(text: str) -> Path:
    """`run` subcommand: parse -> clarify gate (BLOCKING per BRAIN.md) -> build."""
    spec = parse_request(text)
    qs = open_questions(spec)
    if qs:
        if sys.stdin.isatty():
            confirmed = confirm_interactive(spec)
            if confirmed is None:
                print(
                    "Спека не подтверждена — перезапусти с уточнённым запросом "
                    "(или дай brain-сессии перепарсить).",
                    file=sys.stderr,
                )
                sys.exit(4)
            spec = confirmed
        else:
            # Non-interactive caller: surface the questions, NEVER silently
            # build with missing dims (BRAIN.md: clarify is blocking).
            print(restate(spec), file=sys.stderr)
            print("Вопросы:", file=sys.stderr)
            for q in qs:
                print(f"  - {q}", file=sys.stderr)
            sys.exit(3)
    return run_spec(spec, _spec_out_dir(spec))


def run_ping() -> None:
    """`ping` subcommand (BRAIN.md step 0): warn, never block — exit 0 either way."""
    from agent import printer  # lazy: pulls in bambulabs-api/paho

    cfg = load_config()
    if not printer_configured(cfg):
        print(
            "printer not configured — fill A1_IP / A1_SERIAL / A1_ACCESS_CODE in .env "
            "(A1 screen -> LAN Mode + Developer Mode). Slicing works without it."
        )
    elif printer.ping(cfg):
        print(f"printer reachable at {cfg.a1_ip}:{printer.MQTT_PORT}")
    else:
        print(
            f"printer UNREACHABLE at {cfg.a1_ip}:{printer.MQTT_PORT} — A1 off or on "
            "another network? Slicing still works; send the .gcode.3mf later."
        )


def run_send(gcode_3mf: Path) -> None:
    """`send` subcommand (BRAIN.md step 7): FTPS upload + MQTT project_file start."""
    from agent import printer  # lazy: pulls in bambulabs-api/paho

    cfg = load_config()
    if not printer_configured(cfg):
        print(
            "printer not configured (fill A1_IP / A1_SERIAL / A1_ACCESS_CODE in .env) — "
            f"open {gcode_3mf} in Bambu Studio/Handy manually."
        )
        return  # exit 0: not an error, just no printer yet
    gcode_3mf = Path(gcode_3mf)
    if not gcode_3mf.is_file():
        print(f"FATAL: no such file: {gcode_3mf}", file=sys.stderr)
        sys.exit(2)
    printer.handoff(cfg, gcode_3mf)
    print(
        f"sent {gcode_3mf.name} -> {printer.remote_ftp_path(gcode_3mf)} on {cfg.a1_ip}; "
        "print started — готово к проверке в Bambu Handy"
    )


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="agent.pipeline", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("parse", help="heuristic parse -> BuildSpec JSON draft on stdout")
    p.add_argument("request", help="print request text")

    s = sub.add_parser("spec", help="confirmed spec.json -> generate/gate/slice")
    s.add_argument("spec_file", type=Path, help="path to BuildSpec JSON")

    v = sub.add_parser(
        "verify", help="spec.json -> generate/gate/render -> rubric JSON (no slice)"
    )
    v.add_argument("spec_file", type=Path, help="path to BuildSpec JSON")

    r = sub.add_parser("run", help="parse -> clarify gate -> build")
    r.add_argument("request", help="print request text")

    g = sub.add_parser("gear", help="spur gear Ø20 end-to-end (CAD -> gate -> slice)")
    g.add_argument("--count", type=int, default=1, help="number of separate gears")

    sub.add_parser("ping", help="printer reachability check (never blocks; exit 0)")

    sd = sub.add_parser("send", help="upload .gcode.3mf to the A1 (FTPS) and start the print (MQTT)")
    sd.add_argument("gcode_3mf", type=Path, help="path to a sliced .gcode.3mf")

    args = ap.parse_args(argv)
    if args.cmd == "parse":
        print(spec_to_json(parse_request(args.request)))
    elif args.cmd == "spec":
        run_from_file(args.spec_file)
    elif args.cmd == "verify":
        run_verify(args.spec_file)
    elif args.cmd == "run":
        run_request(args.request)
    elif args.cmd == "gear":
        run_gear(args.count)
    elif args.cmd == "ping":
        run_ping()
        sys.exit(0)
    elif args.cmd == "send":
        run_send(args.gcode_3mf)


if __name__ == "__main__":
    main()
