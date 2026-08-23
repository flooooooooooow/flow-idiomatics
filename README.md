# Flow Idiomatics

> This is not an examples bank.
>
> This repository exists to show what Flow looks like when the problem is difficult enough that the language starts paying rent.

Flow is most interesting at the point where ordinary syntax would usually collapse into framework plumbing, ownership ceremony, callback topology, solver glue, dependency injection, control-system scaffolding, or a pile of mutually unaware libraries.

`flow-idiomatics` lives at that boundary.

The programs here are intentionally close to the **maximum useful WTF density** of the language: dense enough to expose Flow's unusual abstractions, but still written the way a serious Flow program should be written. The goal is not code golf. The goal is to make difficult systems look like the systems they describe.

Flow 1.0.0 deliberately keeps a small Stable production core. Several of the features showcased here — algebraic effects, dynamics/control DSLs, declarative planning, advanced concurrency, GPU surfaces and autodiff — are currently Experimental in the main Flow repository. This repo treats that status as a constraint, not an excuse to blur reality. Every showcase states its required host/backend, and the CI is intended to compile or run the examples against current Flow rather than blessing invented syntax.

## What belongs here

| Area | Question this repository answers |
|---|---|
| `showcases/` | What happens when we push Flow syntax until it is almost unreasonable, but still idiomatic? |
| `maximal/` | Which complex Flow features can coherently coexist in one program on a specific target? |
| `comparisons/` | What does the same architectural idea cost in Rust, C++, Python, TypeScript, MATLAB-style tooling, or conventional framework code? |
| `STYLE.md` | Which forms are technically valid but spiritually wrong in Flow? |
| `benchmarks/` | What is actually fast, under a reproducible benchmark, rather than what we would like to be fast? |

## The standard

A showcase should earn its complexity. A program qualifies when it demonstrates at least one of the following: behaviour selected by scoped capabilities instead of parameter plumbing; a dynamical model that is also executable deployment code; borrowed memory without ownership noise; declarative ordering/search where the compiler owns plan selection; pattern matching that removes state-machine scaffolding; real-time or systems constraints expressed in the program rather than comments; or several of those properties interacting in one coherent design.

A maximal program has a stricter standard. It must combine multiple advanced language surfaces without becoming a feature checklist. If removing a feature makes the architecture clearer, that feature did not belong there.

## The three kinds of complexity

Flow is at its best when it removes **incidental complexity** while leaving **domain complexity** visible. This repository deliberately keeps domain complexity high. It also includes a third category: **language-boundary complexity**, where several experimental features collide and expose what Flow can or cannot currently express cleanly.

That distinction matters. A 40-line Flow program is not automatically better than a 100-line Rust program. It is better only when the missing 60 lines were ceremony rather than meaning.

## Current showcase map

The first set is organised around four pressure tests.

`showcases/effects/order_worlds.flow` demonstrates one body of business logic executing under production, deterministic-test, partially mocked and dynamically overridden worlds with algebraic effects and capabilities.

`showcases/evolution/robot_connect.flow` demonstrates an executable continuous plant, sampled controller and state-broken feedback network using Flow's evolution model and `connect` syntax.

`showcases/memory/borrowed_signal.flow` demonstrates fixed owned storage, read-only spans, mutable spans, static extents and zero-copy slicing without turning the API into raw-pointer soup.

`maximal/edge_of_wtf.flow` is the deliberate collision test: borrowed data, closures, value-producing conditionals, pattern matching, scoped effects, nested handler replacement and explicit cleanup in a single C-target program. It is not intended as a beginner tutorial.

The comparison documents explain why these shapes matter rather than merely showing shorter syntax.

## Performance policy

This repository does not publish decorative benchmark numbers.

A performance claim must identify the Flow revision, compiler host, backend, C compiler and flags, machine/runner, workload, warm-up policy, sample count, validation check and comparison implementation. Benchmarks must verify outputs before timing them. If a Flow program is shorter but slower, the result stays. If a comparison language is faster, the result stays. If an optimisation only works because the benchmark changed semantics, it does not count.

The benchmark harness under `benchmarks/` is the source of truth. README prose may summarize generated results, but hard-coded aspirational speedups are not accepted.

## What this repo is trying to prove

Flow's syntax is not unique because it has a nicer `for` loop. It is unique when the same language can describe memory topology, scoped behaviour, continuous evolution, sampled state changes, declarative data movement and low-level execution without forcing the programmer to mentally translate the system through five different programming models.

The best file in this repository should produce the reaction:

> "That is an unreasonable amount of system in an oddly reasonable amount of code."

That is the bar.
