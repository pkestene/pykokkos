from typing import Tuple

import pykokkos as pk

from parse_args import parse_args


@pk.workunit
def y_init(i, y):
    y[i] = 1

@pk.workunit
def matrix_init(j, M, A):
    for i in range(M):
        A[j][i] = 1

@pk.workunit
def yAx(j, acc, M, y, x, A):
    temp2: float = 0
    for i in range(M):
        temp2 += A[j][i] * x[i]

    acc += y[j] * temp2

def run() -> None:
    values: Tuple[int, int, int, int, int, bool] = parse_args()
    N: int = values[0]
    M: int = values[1]
    fill: bool = values[-1]
    nrepeat: int = 100
    print(f"Total size S = {N * M} N = {N} M = {M}")

    pk.set_default_space(pk.ExecutionSpace.Cuda)

    y: pk.View1D = pk.View([N], pk.double)
    x: pk.View1D = pk.View([M], pk.double)
    A: pk.View2D = pk.View([N, M], pk.double)

    p = pk.RangePolicy(pk.get_default_space(), 0, N)
    pk.parallel_for(p, y_init, y=y)
    pk.parallel_for(pk.RangePolicy(pk.get_default_space(), 0, M), y_init, y=x)
    pk.parallel_for(p, matrix_init, M=M, A=A)

    # if fill:
    #     y.fill(1)
    #     x.fill(1)
    #     A.fill(1)
    # else:
    #     for i in range(N):
    #         y[i] = 1

    #     for i in range(M):
    #         x[i] = 1

    #     for j in range(N):
    #         for i in range(M):
    #             A[j][i] = 1

    timer = pk.Timer()

    for i in range(nrepeat):
        result = pk.parallel_reduce(p, yAx, M=M, y=y, x=x, A=A)

    timer_result = timer.seconds()

    print(f"Computed result for {N} x {M} is {result}")
    solution: float = N * M

    if result != solution:
        pk.printf("Error: result (%lf) != solution (%lf)\n",
                  result, solution)

    print(f"N({N}) M({M}) nrepeat({nrepeat}) problem(MB) time({timer_result}) bandwidth(GB/s)")

if __name__ == "__main__":
    run()
