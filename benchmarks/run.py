#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math
import os
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
KERNEL = ROOT / "numeric_kernel"


@dataclass
class Target:
    name: str
    command: list[str]


def run_checked(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def compile_targets(flow_root: Path, build: Path) -> tuple[list[Target], list[tuple[str, str]]]:
    build.mkdir(parents=True, exist_ok=True)

    flow_driver = flow_root / "flow"
    if not flow_driver.exists():
        raise SystemExit(f"Flow driver not found: {flow_driver}")

    generated_c = build / "kernel.flow.c"
    run_checked(
        [str(flow_driver), "tool", "compiler/scripts/flowc_emit.flow", str(KERNEL / "kernel.flow"), str(generated_c)],
    )

    cc = shutil.which("cc")
    cxx = shutil.which("c++") or shutil.which("g++")
    rustc = shutil.which("rustc")

    if cc is None:
        raise SystemExit("A C compiler is required to benchmark Flow's C backend")

    flow_binary = build / "flow-kernel"
    run_checked([cc, "-O3", "-std=c11", "-D_POSIX_C_SOURCE=200809L", str(generated_c), "-lm", "-o", str(flow_binary)])

    targets = [Target("Flow/C", [str(flow_binary)])]
    skipped: list[tuple[str, str]] = []

    if cxx is not None:
        try:
            cpp_binary = build / "cpp-kernel"
            # Use libstdc++ explicitly since clang may not find libc++ stdlib
            run_checked([cxx, "-O3", "-std=c++20", "-stdlib=libstdc++", str(KERNEL / "kernel.cpp"), "-o", str(cpp_binary)])
            targets.append(Target("C++20", [str(cpp_binary)]))
        except subprocess.CalledProcessError as e:
            reason = f"C++ compilation failed: {e.stderr if hasattr(e, 'stderr') else 'unknown error'}"
            skipped.append(("C++20", reason))
            print(f"::warning::Skipping C++20 benchmark: compilation failed", file=sys.stderr)

    if rustc is not None:
        try:
            rust_binary = build / "rust-kernel"
            run_checked([rustc, "-C", "opt-level=3", str(KERNEL / "kernel.rs"), "-o", str(rust_binary)])
            targets.append(Target("Rust", [str(rust_binary)]))
        except subprocess.CalledProcessError as e:
            reason = f"Rust compilation failed: {e.stderr if hasattr(e, 'stderr') else 'unknown error'}"
            skipped.append(("Rust", reason))
            print(f"::warning::Skipping Rust benchmark: compilation failed", file=sys.stderr)

    targets.append(Target("CPython", [sys.executable, str(KERNEL / "kernel.py")]))
    return targets, skipped


def parse_result(output: str) -> float:
    line = output.strip().splitlines()[-1]
    return float(line)


def timed_run(target: Target) -> tuple[float, float]:
    start = time.perf_counter_ns()
    result = run_checked(target.command)
    stop = time.perf_counter_ns()
    return (stop - start) / 1_000_000.0, parse_result(result.stdout)


def benchmark(target: Target, samples: int) -> tuple[float, float, list[float]]:
    _, warm_value = timed_run(target)
    times: list[float] = []
    value = warm_value

    for _ in range(samples):
        elapsed_ms, value = timed_run(target)
        times.append(elapsed_ms)

    return statistics.median(times), value, times


def validate(values: dict[str, float]) -> None:
    reference = values["Flow/C"]
    tolerance = max(1.0e-9, abs(reference) * 1.0e-9)

    for name, value in values.items():
        if not math.isclose(reference, value, rel_tol=1.0e-9, abs_tol=tolerance):
            raise SystemExit(
                f"Semantic mismatch: Flow/C={reference:.12f}, {name}={value:.12f}"
            )


def flow_revision(flow_root: Path) -> str:
    try:
        result = run_checked(["git", "rev-parse", "HEAD"], cwd=flow_root)
        return result.stdout.strip()
    except Exception:
        return "unknown"


def render_report(
    flow_root: Path,
    samples: int,
    medians: dict[str, float],
    values: dict[str, float],
    skipped: list[tuple[str, str]],
) -> str:
    flow_ms = medians["Flow/C"]
    lines = [
        "# Numeric kernel benchmark",
        "",
        f"Flow revision: `{flow_revision(flow_root)}`",
        "",
        f"Workload: 20,000,000 ordered `f64` recurrence steps. One untimed warm-up plus {samples} timed process runs per implementation. Median wall-clock time is reported. All implementations must produce numerically equivalent output before results are emitted.",
        "",
        "| Implementation | Median | Relative to Flow | Result |",
        "|---|---:|---:|---:|",
    ]

    for name, median_ms in medians.items():
        relative = median_ms / flow_ms
        lines.append(
            f"| {name} | {median_ms:.3f} ms | {relative:.3f}x | {values[name]:.12f} |"
        )

    lines.extend(
        [
            "",
            "Lower time is better. `Relative to Flow` is elapsed-time ratio, so values above `1.0x` are slower than Flow for this workload and values below `1.0x` are faster.",
            "",
            "This benchmark measures generated native execution plus process startup. It does not measure Flow compile time. No `-ffast-math`, target-specific ISA flag or semantics-changing optimisation is enabled.",
        ]
    )
    
    if skipped:
        lines.extend(
            [
                "",
                "## Skipped implementations",
                "",
            ]
        )
        for name, reason in skipped:
            lines.append(f"- **{name}**: {reason}")
    
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flow-root", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--output", type=Path, default=ROOT / "benchmark-results.md")
    args = parser.parse_args()

    if args.samples < 1:
        raise SystemExit("--samples must be at least 1")

    build = ROOT / ".build"
    targets, skipped = compile_targets(args.flow_root.resolve(), build)

    medians: dict[str, float] = {}
    values: dict[str, float] = {}

    for target in targets:
        median_ms, value, _ = benchmark(target, args.samples)
        medians[target.name] = median_ms
        values[target.name] = value

    validate(values)
    report = render_report(args.flow_root.resolve(), args.samples, medians, values, skipped)
    args.output.write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
