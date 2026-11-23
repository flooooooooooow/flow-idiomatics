# flowc C Generation Bug: Closure Capture Type Confusion

## Failing Showcase
`maximal/algebraic_core.flow`

## Error
```
algebraic_core.c:728:24: error: invalid operands to binary expression ('fn_i32__i32' and 'int32_t' (aka 'int'))
  728 |   return ((_env->scale * x) + _env->bias);
      |            ~~~~~~~~~~~ ^ ~
```

## Root Cause
The flowc C backend has a type confusion bug when composing closures:
1. `compose()` returns a closure that captures two function values `outer` and `inner` (both type `(i32) -> i32`)
2. `affine()` returns a closure that captures scalar values `scale: i32` and `bias: i32`
3. When an `affine` closure is passed through `compose`, flowc incorrectly generates C code treating `_env->scale` as function pointer type `fn_i32__i32` instead of `i32`

Minimal repro: `.github/known-failures/minimal_repro_closure_bug.flow`

## Status
- Passed on Sept 10, 2026 with Python-hosted compiler (FLOW_HOST=python)
- Fails with native flowc compiler (current)
- **Fix needed in**: https://github.com/flooooooooooow/flow (compiler)

## Workaround
CI marks this test as allowed-to-fail until the flowc compiler is fixed.
