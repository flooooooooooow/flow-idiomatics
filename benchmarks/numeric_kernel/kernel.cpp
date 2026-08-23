#include <cstdio>

static double run_kernel(int iterations)
{
    double x = 0.5;
    double y = 1.25;

    for (int i = 0; i < iterations; ++i)
    {
        x = x * 1.0000001 + y * 0.0000003;
        y = y * 0.9999999 + x * 0.0000002;
    }

    return x + y;
}

int main()
{
    const double result = run_kernel(20000000);
    std::printf("%.12f\n", result);
    return 0;
}
