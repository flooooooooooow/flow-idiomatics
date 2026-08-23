# Feature Collision Matrix

The point of the `maximal/` directory is not to collect isolated syntax cards. It is to show advanced features surviving contact with one another.

| Feature | `edge_of_wtf.flow` | `adaptive_pipeline.flow` | `evolving_effectful_system.flow` |
|---|:---:|:---:|:---:|
| Fixed owned arrays | ✓ |  |  |
| `span<T>` borrowed views | ✓ |  |  |
| `span<mut T>` mutation | ✓ |  |  |
| Static span extent | ✓ |  |  |
| Zero-copy slicing | ✓ |  |  |
| Explicit `ptr<T>` | ✓ |  | generated step uses address-of |
| `defer` cleanup | ✓ |  |  |
| Escaping closure | ✓ |  |  |
| Higher-order function | ✓ |  |  |
| Value-producing `if` | ✓ |  |  |
| Guarded `match` | ✓ | ✓ | ✓ |
| Alternating match arms | ✓ | ✓ | ✓ |
| Algebraic effects | ✓ | ✓ | ✓ |
| Multi-effect capability | ✓ |  |  |
| Nested handler override | ✓ | ✓ | ✓ |
| Named pipeline fork |  | ✓ |  |
| Placeholder `_` in pipeline |  | ✓ |  |
| `choose` pipeline topology |  | ✓ |  |
| Enum-driven dataflow |  | ✓ |  |
| Continuous `evolves as` state |  |  | ✓ |
| Sampled `every` / `becomes` state |  |  | ✓ |
| Nested `flow` composition |  |  | ✓ |
| `connect` topology |  |  | ✓ |
| Generated `*_new` / `*_step` API |  |  | ✓ |

The standalone showcases add one important collision that is intentionally kept out of the table above: `showcases/evolution/hybrid_bounce.flow` combines continuous RK4 evolution with a discrete `when ... reaches` reset.

## Why there are three maximal programs

A single file containing every feature Flow has would be less honest than these three.

Flow 1.0.0 has a Stable core and several Experimental surfaces with different backend/host requirements. Declarative pipeline expansion is a Python-hosted compiler surface. Dynamics and control syntax is also expanded by the Python host. Metal `@gpu` code generation has a different target contract. Native threading and OS APIs depend on the platform. MLIR does not have complete parity with the C path.

So “all features simultaneously” is defined here as **all advanced features that form a coherent compilation and execution contract for the problem being demonstrated**.

That gives three useful stress directions.

`edge_of_wtf.flow` asks whether Flow can remain readable when low-level ownership, zero-copy borrowing, higher-order code and scoped effects all collide.

`adaptive_pipeline.flow` asks whether declarative computation topology can coexist with ordinary types, classification logic and environment-selected observation.

`evolving_effectful_system.flow` asks whether an executable continuous/sampled control model can coexist with ordinary program control flow and dynamically replaceable telemetry.

If Flow later makes more advanced surfaces share one supported compilation contract, this matrix should get denser. The repository should never fake that density before the compiler does.
