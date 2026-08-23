def run_kernel(iterations: int) -> float:
    x = 0.5
    y = 1.25

    for _ in range(iterations):
        x = x * 1.0000001 + y * 0.0000003
        y = y * 0.9999999 + x * 0.0000002

    return x + y


if __name__ == "__main__":
    print(f"{run_kernel(20_000_000):.12f}")
