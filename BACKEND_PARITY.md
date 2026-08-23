# Backend parity contract

A program in this repository may be described as **portable Flow** only when the same source file passes both backend lanes without source rewriting or feature substitution.

## C lane

The program must lower through the C backend, compile to a native executable, run, and satisfy its own semantic checks.

```text
Flow source -> C -> native object/executable -> execute -> semantic assertions pass
```

A successful transpile alone is not evidence of C support.

## MLIR lane

The same source file must lower through the MLIR backend and the emitted module must be accepted by the pinned MLIR verifier.

```text
Flow source -> MLIR -> mlir-opt verification
```

A zero exit status from the Python MLIR generator is not sufficient. The generated module may not contain unresolved placeholders, malformed SSA, invalid dominance, or backend-only pseudo-IR.

## What parity means

Parity is semantic, not textual. C and MLIR are free to use different internal representations when those representations preserve the same Flow-level behavior and ABI contract.

Examples:

- `span<T>` may be represented differently internally, but it remains a borrowed contiguous `{data, length}` view with the same mutability and indexing semantics.
- first-class Flow function values may use backend-native machinery, but an escaping closure must preserve its function and captured environment on both backends.
- match bindings, wildcards, guards, or-patterns, effects, dynamics, and pipelines must preserve source semantics rather than being rewritten out of the showcase for one backend.

## Backend-specific programs

A program that intentionally relies on a target-only facility is allowed, but it must live behind an explicit target/backend label and must not be counted as evidence for portable Flow.

The default is portability. A missing lowering for otherwise general Flow syntax is a compiler parity bug, not a reason to weaken the example.

## CI is the claim

The authoritative portable corpus is the program list in `.github/workflows/ci.yml`. Every entry is executed through C and independently lowered and verified through MLIR. If either lane is red, the repository must not describe that entry as dual-backend portable.
