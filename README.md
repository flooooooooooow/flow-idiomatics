# Flow Idiomatics

> This is not an examples bank.
>
> This repository exists to show what Flow looks like when the problem is difficult enough that the language starts paying rent.

Flow is most interesting at the point where ordinary syntax would usually collapse into framework plumbing, ownership ceremony, callback topology, solver glue, dependency injection, control-system scaffolding, or a pile of mutually unaware libraries.

`flow-idiomatics` lives at that boundary.

The programs here are intentionally close to the **maximum useful WTF density** of the language: dense enough to expose Flow's unusual abstractions, but still written the way a serious Flow program should be written. The goal is not code golf. The goal is to make difficult systems look like the systems they describe.

Flow 1.0.0 deliberately keeps a small Stable production core. Several of the features showcased here — algebraic effects, dynamics/control DSLs, declarative planning, advanced concurrency, GPU surfaces and autodiff — are currently Experimental in the main Flow repository. This repo treats that status as a constraint, not an excuse to blur reality. Every showcase states its required host/backend, and CI runs the programs against current Flow rather than blessing invented syntax.

## What belongs here

| Area | Question this repository answers |
|---|---|
| `showcases/` | What happens when we push Flow syntax until it is almost unreasonable, but still idiomatic? |
| `maximal/` | Which complex Flow features can coherently coexist in one program on a specific target? |
| `comparisons/` | What does the same architectural idea cost in Rust, C++, Python, TypeScript, MATLAB-style tooling, or conventional framework code? |
| `STYLE.md` | Which forms are technically valid but spiritually wrong in Flow? |
| `benchmarks/` | What is actually fast, under a reproducible benchmark, rather than what we would like to be fast? |

## The standard

A showcase should earn its complexity. A program qualifies when it demonstrates behaviour selected by scoped capabilities instead of parameter plumbing, a dynamical model that is also executable deployment code, borrowed memory without ownership noise, declarative computation topology, hybrid continuous/discrete evolution, pattern matching that removes state-machine scaffolding, low-level lifetime control, higher-order composition that replaces callback scaffolding, or several of those properties interacting in one coherent design.

A maximal program has a stricter standard. It must combine multiple advanced language surfaces without becoming a feature checklist. If removing a feature makes the architecture clearer, that feature did not belong there.

## Portable means two backends

A file listed in `portable-programs.txt` has a mechanical contract, not a marketing label. CI must execute that exact source through Flow's C/native backend and independently lower it through the MLIR backend. The emitted MLIR must be non-empty and accepted by LLVM's `mlir-opt`.

That distinction matters because successful code generation is weaker than valid intermediate representation. The portable corpus is deliberately adversarial: when it exposes a backend gap, the compiler is fixed rather than the showcase being simplified. `portable-programs.txt` is the single source of truth for both lanes.

## The three kinds of complexity

Flow is at its best when it removes **incidental complexity** while leaving **domain complexity** visible. This repository deliberately keeps domain complexity high. It also includes a third category: **language-boundary complexity**, where several experimental features collide and expose what Flow can or cannot currently express cleanly.

That distinction matters. A 40-line Flow program is not automatically better than a 100-line Rust program. It is better only when the missing 60 lines were ceremony rather than meaning.

## Current showcase map

| Program | Pressure test |
|---|---|
| `showcases/effects/packet_admission_worlds.flow` | One admission algorithm under live, panic and deterministic worlds; multi-effect capabilities; composed handlers; nested dynamic replacement. |
| `showcases/memory/borrowed_signal.flow` | Fixed ownership, immutable and mutable spans, static extents, zero-copy slices, value-producing conditionals and guarded matching. |
| `showcases/evolution/closed_loop_motor.flow` | Continuous plant, sampled controller and state-broken feedback network using generated evolution APIs and `connect`. |
| `showcases/evolution/hybrid_bounce.flow` | RK4 continuous evolution plus a discrete `when ... reaches` reset in one hybrid model. |
| `maximal/edge_of_wtf.flow` | Spans, explicit heap ownership, `defer`, escaping closures, higher-order calls, matching, value-producing `if`, effects and nested handler replacement in one portable program. |
| `maximal/adaptive_pipeline.flow` | Named fork records, placeholder pipelines, `choose`, enums, guarded matching and scoped observation in one dataflow. |
| `maximal/evolving_effectful_system.flow` | Continuous dynamics, sampled control, nested flow topology, generated stepping, effects, handler replacement and classification in one executable system. |
| `maximal/algebraic_core.flow` | Escaping affine closures, closure composition where a closure captures other closures, fold-map over spans, algebraic classification and an effectful observation shell around a pure higher-order core. |

The maximal directory is intentionally plural. There is no honest “all features at once” file because some advanced surfaces still have different host or target contracts. A Metal `@gpu` kernel and a native CPU program are not the same compilation problem. The useful challenge is to combine everything that coherently belongs on one target, then make portability claims executable where portability is promised.

## Algebra before branch soup

Flow can express ordinary imperative control flow, but that is not automatically the most revealing architecture. When behaviour itself is data, prefer first-class functions. When two transformations are one conceptual program, compose them. When a loop is really a fold, keep the loop local to the fold and pass the transformation and reduction policy as values. When a value is being classified, use matching. When the outside world changes, put that change in an effect handler rather than infecting the pure core with mode flags.

`maximal/algebraic_core.flow` is the reference pressure test for this style. Its `compose` returns an escaping closure that owns two other first-class function values; `fold_map` contains the necessary iteration while the transformation pipeline remains algebraic; observation is selected by nested capability scopes rather than parameters. This is deliberately Haskell-esque in architecture without pretending Flow is Haskell or inventing syntax Flow does not have.

## Cross-language comparisons

`comparisons/README.md` contains direct architectural comparisons for scoped effects versus Rust trait plumbing, temporary handler overrides versus mutable application configuration, spans versus C pointer/count APIs and C++20 `std::span`, continuous plant/controller systems versus Python/SciPy orchestration, hybrid event resets versus manual integration loops, pattern matching versus branch accumulation, `defer` versus mirrored cleanup paths, and declarative sort/search versus explicitly selected library algorithms.

The comparisons are not scored by token count. They ask whether missing lines were ceremony or semantics.

## Do and don't

`STYLE.md` is the opinionated half of the repository. It shows why ordinary mutable state should remain ordinary data, why environmental behaviour belongs in effects, why higher-order policies should be represented as function values rather than switch ladders, why `span<mut T>` should communicate actual mutation, why `flow` should represent real evolution rather than replace every numerical loop, why sampling periods should not hide in counter arithmetic, why `connect` should expose topology, why cleanup should bind to scope, and why examples must not invent future Flow syntax.

## Performance policy

This repository does not publish decorative benchmark numbers.

A performance claim must identify the Flow revision, compiler host, backend, compiler flags, runner, workload, warm-up policy, sample count, validation check and comparison implementation. Benchmarks verify outputs before timing results are emitted. If Flow is shorter but slower, the result stays. If C++ or Rust is faster, the result stays. If an optimisation changes semantics, it does not count.

The first benchmark under `benchmarks/numeric_kernel/` runs the same 20,000,000-step ordered `f64` recurrence in Flow-generated C, C++20, Rust and CPython. `benchmarks/run.py` transpiles Flow, compiles native implementations, performs an untimed warm-up, takes repeated wall-clock samples, validates numerical equivalence and generates a Markdown result table. CI publishes that table into the Actions job summary with the exact Flow revision.

The benchmark harness is the source of truth. README prose may summarize generated results later, but hard-coded aspirational speedups are not accepted.

## What this repo is trying to prove

Flow's syntax is not unique because it has a nicer `for` loop. It is unique when the same language can describe memory topology, scoped behaviour, higher-order programs, continuous evolution, sampled state changes, hybrid events, declarative data movement and low-level execution without forcing the programmer to mentally translate the system through five different programming models.

The best file in this repository should produce the reaction:

> "That is an unreasonable amount of system in an oddly reasonable amount of code."

That is the bar.
