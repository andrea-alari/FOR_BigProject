import mip
import Helper_functions
from Helper_functions import print_result, distance_calc


def int_solve(data):
    M = data["M"]  # max energy production (kWh)
    Q = data["Q"]  # energy produced by a ton of corn chopping (kWh/t)
    a = data["a"]  # percentage of dry matter in chopping from farm i∈I
    b = data["b"]  # revenue per unit of energy (€/kWh)
    c = data["c"]  # tons of corn chopping available for each i∈I (t)
    kmax = data["kmax"]  # max percentage of dry matter for fermentation
    kmin = data["kmin"]  # min percentage of dry matter for fermentation
    n = data["n"]  # number of farms
    p = data["p"]  # number of plants to locate
    points = data["points"]  # coordinates of farm i∈I

    N = range(n)

    # TODO this could be done in a faster way
    dist = distance_calc(points)

    m = mip.Model()
    m.verbose = 0
    X = [[m.add_var(var_type=mip.BINARY) for _ in N] for _ in N]
    Y = [m.add_var(var_type=mip.BINARY) for _ in N]
    F = [[m.add_var() for _ in N] for _ in N]

    # constraints
    m.add_constr(mip.xsum(Y[i] for i in N) == p)

    for i in N:
        for j in N:
            m.add_constr(F[i][j] <= c[i] * X[i][j])

    for i in N:
        m.add_constr(mip.xsum(X[i][j] for j in N) <= 1)
        m.add_constr(mip.xsum(X[j][i] for j in N) <= n * Y[i])

    for j in N:
        m.add_constr(mip.xsum(F[i][j] for i in N) <= M / Q * Y[j])
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) <= kmax * mip.xsum(F[i][j] for i in N))
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) >= kmin * mip.xsum(F[i][j] for i in N))

    m.objective = mip.maximize(
        mip.xsum(F[i][j] * Q * b - dist[i, j] * X[i][j] for j in N for i in N))

    m.optimize()
    print(m.objective_value)
    for i in N:
        print(Y[i].x)
    #print_result(m, X, Y, F, N, points)

    return m.objective_value


def linear_relaxation(data):
    m, Y, X, F, dist, points = Helper_functions.model_creation(data)
    N = range(len(Y))

    m.optimize()
    print(m.objective_value)

    eps = 1e-5

    while True:
        m.optimize()
        pair = None  # Initialize pair to None, leave the loops

        for i in N:
            for j in N:
                # Check if inequality is violated (Add an epsilon to avoid numerical problems)
                if Y[j].x is None or X[i][j].x is None:
                    break
                if X[i][j].x > Y[j].x + eps:
                    pair = (i, j)
                    break  # Leave the inner loop
            if pair is None:
                break  # Leave the outer loop if an inequality is found
        if pair is None:
            break  # No violated inequality was found, leave the loop
        i, j = pair
        m.add_constr(X[i][j] <= Y[j])

    print_result(m, X, Y, F, N, points)

    return m.objective_value
