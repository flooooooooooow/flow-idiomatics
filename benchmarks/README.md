# Benchmarks

This directory exists so “Flow is fast” can be either measured or rejected.

The benchmark rule is simple: architecture may be interesting elsewhere; benchmark kernels must be boring enough that semantic equivalence is obvious.

## Numeric kernel

`numeric_kernel/` contains the same ordered double-precision recurrence in Flow, C++20, Rust and CPython. Every implementation performs 20,000,000 iterations and prints the final `f64` result.

The harness transpiles Flow to C, compiles the generated C with `-O3`, compiles the C++ and Rust variants with their ordinary high-optimisation settings, warms every executable once, times repeated process runs, validates numerical equivalence and reports the median wall-clock duration.

No `-ffast-math`, target-specific ISA flag, profile-guided optimisation or semantics-changing arithmetic mode is enabled. The intention is to compare ordinary optimised native output before trying to manufacture a win.

Run it from a checkout of this repository with a checkout of Flow available locally:

```bash
python benchmarks/run.py --flow-root ../flow --samples 5
```

The generated `benchmarks/benchmark-results.md` is deliberately not hand-maintained. CI writes the same report into the GitHub Actions job summary so a performance claim always has a runner, Flow revision and workload attached to it.

## What the number means

The reported duration includes process startup because every implementation is timed as an executable command. At 20,000,000 recurrence steps the compute kernel is intended to dominate that fixed cost, but this benchmark is still not a microarchitectural cycle counter.

It does not measure compiler throughput. It does not prove Flow is faster in general. It does not measure effect dispatch, span bounds behaviour, dynamics expansion, GPU execution, allocator performance, I/O, threads, SIMD or cache-heavy data structures.

Those deserve separate benchmarks with separate semantic checks.

## Benchmark admission rule

A new benchmark belongs here only when the comparison implementations compute the same result, use the same algorithmic complexity, run the same problem size, validate output before timing claims are surfaced, record the Flow revision and compiler/backend path, avoid hidden setup in only one implementation, and keep unfavourable results.

If the interesting claim is “Flow expresses this architecture more directly,” put it in `comparisons/`. If the claim is “Flow executes this workload faster,” it belongs here and needs a number.
