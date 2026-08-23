# Flow Versus the Usual Shape of the Problem

These are architectural comparisons, not syntax beauty contests. The other languages are not being written badly on purpose. The point is to identify which concepts have first-class representation in Flow and therefore disappear from user-level scaffolding.

## 1. Environment-selected behaviour: Flow effects vs Rust trait plumbing

### Flow

```flow
effect Clock {
    now() -> i32,
}

effect Log {
    info(message: string) -> void,
}

function process(packet: i32) -> void {
    Log.info("processing")
    let t: i32 = Clock.now()
    printf("packet=%d time=%d\n", packet, t)
}

handle Clock with FrozenClock {
    handle Log with ConsoleLog {
        process(42)
    }
}
```

`process` names the effects it performs through the effect interfaces. The surrounding scope selects their implementations. Deep intermediate callers do not acquire `clock` and `log` parameters solely to forward them.

### Rust

```rust
trait Clock {
    fn now(&self) -> i32;
}

trait Log {
    fn info(&self, message: &str);
}

fn process<C: Clock, L: Log>(packet: i32, clock: &C, log: &L) {
    log.info("processing");
    let t = clock.now();
    println!("packet={packet} time={t}");
}
```

This is excellent Rust. The cost is architectural: dependencies become parameters, generic bounds or trait objects, and those dependencies propagate through the call graph unless a container or global mechanism is introduced.

Flow's advantage is not that `effect` is fewer characters than `trait`. It is that scoped environmental behaviour is a language-level control mechanism.

## 2. Temporary override: Flow dynamic handler scope vs global/config mutation

### Flow

```flow
handle Log with OpsLogger {
    Log.info("visible")

    handle Log with SilentLogger {
        sensitive_region()
    }

    Log.info("visible again")
}
```

The inner override is lexical and the outer implementation is restored automatically.

### Conventional application configuration

```cpp
const auto old = logger.mode();
logger.setMode(Logger::Silent);
sensitiveRegion();
logger.setMode(old);
```

This can be made safe with RAII, but then the program needs an RAII guard type whose purpose is to reconstruct a scoped semantic that Flow already has.

## 3. Borrowed signal processing: Flow spans vs C pointer/count APIs

### Flow

```flow
function gain(samples: span<mut f32>, amount: f32) -> void {
    let mut i: i32 = 0
    while i < samples.len {
        samples[i] = samples[i] * amount
        i = i + 1
    }
}

let mut frame: array<f32, 8> = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
gain(frame[2..6], 0.5)
```

The callee gets a non-owning contiguous mutable view. Length travels with the view. The slice does not allocate or copy.

### C

```c
void gain(float *samples, size_t count, float amount)
{
    for (size_t i = 0; i < count; ++i)
        samples[i] *= amount;
}

float frame[8] = {1,2,3,4,5,6,7,8};
gain(frame + 2, 4, 0.5f);
```

The C version is compact and fast, but `samples` and `count` are two independent values whose relationship is maintained by convention. Flow retains the same low-level shape while giving the borrow a type.

### C++20

```cpp
void gain(std::span<float> samples, float amount)
{
    for (auto& sample : samples)
        sample *= amount;
}
```

This is close to Flow's memory model and is the right comparison. Flow's distinction becomes more interesting when spans coexist with its effect, dynamics and verification surfaces instead of living in a separate library abstraction.

## 4. Continuous plant plus sampled controller: Flow vs manual simulation glue

### Flow

```flow
flow Motor {
    state speed: f64 = 0.0
    input voltage: f64
    output measured_speed: f64 = speed
    param damping: f64 = 0.5

    speed evolves as voltage - damping * speed
}

flow Controller {
    state command: f64 = 0.0
    input setpoint: f64
    input feedback: f64
    output voltage: f64 = command
    param kp: f64 = 2.0

    every 1 ms {
        command becomes kp * (setpoint - feedback)
    }
}

flow ClosedLoop {
    plant: Motor
    controller: Controller

    connect {
        controller.voltage -> plant.voltage
        plant.measured_speed -> controller.feedback
    }
}
```

The source contains the equations, the sampled update and the topology. Those are not comments around a simulation loop; they are the program.

### Python/SciPy-style structure

```python
from scipy.integrate import solve_ivp

DAMPING = 0.5
KP = 2.0
SAMPLE_PERIOD = 0.001

def plant_rhs(t, state, voltage):
    speed, = state
    return [voltage - DAMPING * speed]

def controller(setpoint, feedback):
    return KP * (setpoint - feedback)

speed = 0.0
command = 0.0
setpoint = 1.0

t = 0.0
while t < 5.0:
    command = controller(setpoint, speed)
    result = solve_ivp(
        lambda tau, y: plant_rhs(tau, y, command),
        (t, t + SAMPLE_PERIOD),
        [speed],
        t_eval=[t + SAMPLE_PERIOD],
    )
    speed = result.y[0, -1]
    t += SAMPLE_PERIOD
```

The Python code is perfectly reasonable analysis code. The distinction is that solver orchestration, sampling and wiring are user-level mechanics. In Flow they remain model semantics that the compiler expands.

## 5. Hybrid reset: Flow event semantics vs hand-managed threshold logic

### Flow

```flow
flow Ball {
    state height: f64 = 2.0
    state velocity: f64 = 0.0
    param gravity: f64 = 9.81
    param restitution: f64 = 0.8

    height evolves as velocity
    velocity evolves as -gravity

    when height reaches 0.0 {
        velocity becomes -restitution * velocity
        height becomes 0.0
    }
}
```

Continuous evolution and discrete reset coexist in one model.

### Manual integration

```cpp
for (int i = 0; i < steps; ++i)
{
    velocity += -gravity * dt;
    height += velocity * dt;

    if (height <= 0.0)
    {
        height = 0.0;
        velocity = -restitution * velocity;
    }
}
```

The C++ is easy to understand, but the event is now inseparable from one particular integrator loop and one particular threshold approximation. Flow keeps the event as a model construct and lets the evolution machinery own the stepping policy.

## 6. Classification: Flow pattern matching vs flag accumulation

### Flow

```flow
function severity(score: i32) -> i32 {
    match score {
        0 => { return 0 }
        1 | 2 | 3 => { return 1 }
        x if x < 50 => { return 2 }
        _ => { return 3 }
    }
}
```

### C-style branching

```c
int severity(int score)
{
    if (score == 0)
        return 0;
    if (score == 1 || score == 2 || score == 3)
        return 1;
    if (score < 50)
        return 2;
    return 3;
}
```

This is not a dramatic brevity win. The advantage appears when Flow destructures structs, fixed lists and enum variants in the same match form and can perform exhaustiveness checks on closed domains.

## 7. Cleanup: Flow `defer` vs manually mirrored returns

### Flow

```flow
let data: ptr<i32> = calloc(1024, 4)
if data == null {
    return 1
}
defer free(data)

if validate(data) == 0 {
    return 2
}

consume(data)
return 0
```

### C

```c
int *data = calloc(1024, sizeof(int));
if (!data)
    return 1;

if (!validate(data))
{
    free(data);
    return 2;
}

consume(data);
free(data);
return 0;
```

C++ and Rust have stronger ownership mechanisms than either version above. Flow is not claiming to out-Rust Rust here. The idiom is simply that explicit low-level ownership should not force cleanup logic to be duplicated across control-flow exits.

## 8. Declarative ordering/search: Flow says what, compiler chooses how

### Flow

```flow
values |> sort
values |> sort descending
values |> sort unique
let position: i32 = values |> find(target)
```

Flow's Python-hosted compiler can choose among registered plans using applicability constraints, ordering hints, scratch-space requirements and a cost model. `flow explain` exposes the selected lowering.

### Typical library call

```cpp
std::sort(values.begin(), values.end());
auto it = std::lower_bound(values.begin(), values.end(), target);
```

The C++ is explicit and excellent when the algorithm choice is part of the engineering decision. The Flow form is useful when the required ordering/search result is the semantic contract and plan selection can legitimately belong to the compiler.

## The real comparison

The relevant comparison is not “Flow uses fewer tokens.” A sufficiently aggressive DSL can always win that contest.

The question is whether the abstraction survives contact with deployment. Flow's interesting claim is that effects can lower to direct calls when statically known, spans can remain pointer-plus-length views, evolution syntax expands to ordinary compiled code, explicit pointers remain available, and the result still targets portable C.

That is what the benchmark and verification layer in this repository is intended to test.
