fn run_kernel(iterations: i32) -> f64 {
    let mut x = 0.5_f64;
    let mut y = 1.25_f64;

    for _ in 0..iterations {
        x = x * 1.0000001 + y * 0.0000003;
        y = y * 0.9999999 + x * 0.0000002;
    }

    x + y
}

fn main() {
    let result = run_kernel(20_000_000);
    println!("{result:.12}");
}
