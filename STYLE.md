# Writing Flow Like Flow

Flow can be written like slightly cleaner C, slightly stranger Rust, or Python with types. All three miss the point.

The idiomatic question is not “what syntax is shortest?” It is “which facts belong in the program so the compiler can preserve them?”

## Behaviour that changes by environment

### Don't: thread infrastructure through the domain

```flow
function place_order(
    sku: i32,
    qty: i32,
    logger: Logger,
    clock: Clock,
    inventory: Inventory,
    notifier: Notifier,
) -> i32 {
    # plumbing has become part of the business signature
}
```

### Do: make environmental behaviour an effect

```flow
effect Log {
    info(message: string) -> void,
}

effect Inventory {
    stock_of(sku: i32) -> i32,
}

function place_order(sku: i32, qty: i32) -> i32 {
    Log.info("order received")
    return Inventory.stock_of(sku)
}
```

The data needed to place the order remains explicit. The implementation of logging or inventory access belongs to the surrounding world.

## Higher-order policy

### Don't: encode a transformation program as mode flags and branch ladders

```flow
function transform(x: i32, mode: i32, scale: i32, bias: i32) -> i32 {
    if mode == 0 {
        return x
    }
    if mode == 1 {
        return scale * x
    }
    return scale * x + bias
}
```

The caller knows the behaviour it wants, but the callee is forced to rediscover that choice on every call.

### Do: make behaviour a first-class value

```flow
function affine(scale: i32, bias: i32) -> (i32) -> i32 {
    return |x: i32| -> i32 {
        return scale * x + bias
    }
}

function compose(
    outer: (i32) -> i32,
    inner: (i32) -> i32,
) -> (i32) -> i32 {
    return |x: i32| -> i32 {
        return outer(inner(x))
    }
}
```

An escaping closure is configuration plus behaviour in one typed value. A closure may own other function values when composition is the actual domain structure. Prefer that to rebuilding a callback graph with tags and switches.

## Pure core, effectful shell

### Don't: mix observation policy into every transformation

```flow
function score(x: i32, verbose: bool) -> i32 {
    let y: i32 = x * 3
    if verbose {
        print(y)
    }
    return y
}
```

### Do: keep the transformation pure and move the world to the boundary

```flow
function score(x: i32) -> i32 {
    return x * 3
}

function evaluate(x: i32) -> i32 {
    let y: i32 = score(x)
    Observe.value(y)
    return y
}
```

A handler can then select visible, silent, deterministic or test observation without changing the algebra of the core.

## Folds and iteration

Functional architecture does not mean pretending iteration vanished. A fold over contiguous data still needs to visit the data.

### Don't: spread traversal, transformation and policy across one giant loop

```flow
let mut total: i32 = 0
let mut i: i32 = 0
while i < values.len {
    if mode == 1 {
        total = total + values[i] * 3
    } else {
        total = total + values[i] + 2
    }
    i = i + 1
}
```

### Do: localize mutation to the fold and pass the algebra as values

```flow
function fold_map(
    values: span<i32>,
    initial: i32,
    transform: (i32) -> i32,
    combine: (i32, i32) -> i32,
) -> i32 {
    let mut acc: i32 = initial
    let mut i: i32 = 0
    while i < values.len {
        acc = combine(acc, transform(values[i]))
        i = i + 1
    }
    return acc
}
```

The loop is not a style failure. It is the implementation of a fold. The important part is that traversal mechanics no longer own transformation policy.

## Owned state

### Don't: turn ordinary mutable data into an effect just because effects exist

```flow
effect StackState {
    push(value: i32) -> void,
    pop() -> i32,
}
```

A stack owned by one object is data, not ambient behaviour. Flow capabilities are stateless today; forcing owned mutation through them makes the model worse.

### Do: keep the state ordinary

```flow
struct Stack {
    values: array<i32, 16>,
    top: i32
}
```

Use an effect only when the policy or implementation is meaningfully selected by an enclosing environment.

## Borrowed memory

### Don't: degrade a bounded contiguous view into a raw pointer plus a mystery integer

```flow
function process(data: ptr<f32>, count: i32) -> void {
    # caller and callee must manually keep two values consistent
}
```

### Do: preserve the borrow as a span

```flow
function process(data: span<f32>) -> void {
    let mut i: i32 = 0
    while i < data.len {
        print(data[i])
        i = i + 1
    }
}
```

Use `span<mut T>` only when mutation is part of the API. Use `span<T, N>` when the extent is a real invariant.

## Mutation

### Don't: make every local mutable pre-emptively

```flow
let mut sample_rate: i32 = 48000
let mut channels: i32 = 2
let mut frames: i32 = 512
```

### Do: make mutation visible because it means something

```flow
let sample_rate: i32 = 48000
let channels: i32 = 2
let mut frame_index: i32 = 0
```

`let mut` should tell the reader where state actually evolves.

## Continuous state

### Don't: manually re-create a dynamical-system DSL with bookkeeping variables

```flow
let mut speed: f64 = 0.0
for k in 0 to steps {
    let derivative: f64 = voltage - damping * speed
    speed = speed + dt * derivative
}
```

That is valid numerical code, but the relationship “speed evolves according to this derivative” has been flattened into loop mechanics.

### Do: write the evolution when evolution is the domain

```flow
flow Motor {
    state speed: f64 = 0.0
    input voltage: f64
    param damping: f64 = 0.5

    speed evolves as voltage - damping * speed
}
```

Use an explicit numerical loop when you actually need explicit numerical control. Use `flow` when the continuous system is the thing being described.

## Sampled control

### Don't: bury scheduling semantics inside counters

```flow
if tick % 48 == 0 {
    command = kp * (target - feedback)
}
```

### Do: state the sampling rule

```flow
every 1 ms {
    command becomes kp * (target - feedback)
}
```

The period is now a model fact rather than an arithmetic coincidence.

## Feedback composition

### Don't: write a giant coordinator whose only purpose is copying outputs into inputs

```flow
controller.feedback = motor.speed
motor.voltage = controller.command
step_controller(&controller, dt)
step_motor(&motor, dt)
```

### Do: expose the topology

```flow
flow Robot {
    plant: Motor
    controller: Controller

    connect {
        controller.command -> plant.voltage
        plant.speed_out -> controller.feedback
    }
}
```

A feedback path still has to be state-broken. `connect` is not permission to create an algebraic loop.

## Branch logic

### Don't: accumulate flags when the program is really classifying one value

```flow
let mut kind: i32 = 0
if score < 0 {
    kind = 1
} else {
    if score < 10 {
        kind = 2
    } else {
        kind = 3
    }
}
```

### Do: make the classification shape visible

```flow
match score {
    x if x < 0 => { return 1 }
    0 | 1 | 2 | 3 => { return 2 }
    _ => { return 3 }
}
```

## Cleanup

### Don't: duplicate resource cleanup across every return path

```flow
if failed {
    free(buffer)
    return 1
}
free(buffer)
return 0
```

### Do: bind cleanup to scope

```flow
let buffer: ptr<i32> = calloc(64, 4)
if buffer == null {
    return 1
}
defer free(buffer)
```

The resource lifetime is visible next to acquisition instead of reconstructed from control flow.

## Declarative operations

### Don't: hand-select an algorithm before you have established that the algorithm itself is part of the contract

```flow
# hand-written sort implementation here
```

### Do: express the required result when Flow can own plan selection

```flow
values |> sort
let position: i32 = values |> find(target)
```

Then inspect the plan with `flow explain`. Declarative syntax is not magic; it is useful precisely because the lowering decision is inspectable.

## Effects are scoped, not global switches

### Don't

```flow
set_global_logging_enabled(false)
do_sensitive_work()
set_global_logging_enabled(true)
```

### Do

```flow
handle Log with SilentLogger {
    do_sensitive_work()
}
```

The outer handler is restored automatically when the scope ends.

## Portability is executable

If a flagship is listed in `portable-programs.txt`, it must execute through the C backend and independently produce MLIR accepted by `mlir-opt`. “The generator returned success” is not enough, and a backend gap is not a reason to rewrite the example into a less expressive architecture.

A genuinely target-specific feature should be labelled target-specific. A generally portable language feature should get backend parity.

## Don't invent future Flow

Flow deliberately does not currently have general `async` / `await` syntax. Some advanced surfaces are target- or host-specific. A beautiful example that does not compile is documentation debt.

When a feature is Experimental, say so. When an example requires the Python-hosted compiler, say so. When a backend lacks parity, either label the boundary honestly or fix the backend. When a benchmark loses, keep the number.

That discipline is part of the idiomatics.
