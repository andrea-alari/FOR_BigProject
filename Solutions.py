import mip
import math
from helper_functions import print_result


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
        m.add_constr(mip.xsum(X[j][i] for j in N) <= 500 * Y[i])

    for j in N:
        m.add_constr(mip.xsum(F[i][j] for i in N) <= M / Q * Y[j])
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) <= kmax * mip.xsum(F[i][j] for i in N))
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) >= kmin * mip.xsum(F[i][j] for i in N))

    m.objective = mip.maximize(
        mip.xsum(F[i][j] * Q * b - dist[i, j] * X[i][j] for j in N for i in N))

    m.optimize()
    print(m.objective_value)

    print_result(m, X, Y, F, N, points)

    return m.objective_value


def linear_relaxation(data):
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

    X = [[m.add_var(lb=0, ub=1) for _ in N] for _ in N]
    Y = [m.add_var(lb=0, ub=1) for _ in N]
    F = [[m.add_var() for _ in N] for _ in N]

    # constraints
    m.add_constr(mip.xsum(Y[i] for i in N) == p)

    for i in N:
        for j in N:
            m.add_constr(F[i][j] <= c[i] * X[i][j])

    for i in N:
        m.add_constr(mip.xsum(X[i][j] for j in N) <= 1)
        m.add_constr(mip.xsum(X[j][i] for j in N) <= 500 * Y[i])

    for j in N:
        m.add_constr(mip.xsum(F[i][j] for i in N) <= M / Q * Y[j])
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) <= kmax * mip.xsum(F[i][j] for i in N))
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) >= kmin * mip.xsum(F[i][j] for i in N))

    m.objective = mip.maximize(
        mip.xsum(F[i][j] * Q * b - dist[i, j] * X[i][j] for j in N for i in N))

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
    # print_result(m, X, Y, F, N, points)

    return m.objective_value


# this kind of algorithm doesn't work
def min_cut(data):
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

    X = [[m.add_var(lb=0, ub=1) for _ in N] for _ in N]
    Y = [m.add_var(lb=0, ub=1) for _ in N]
    F = [[m.add_var() for _ in N] for _ in N]

    # constraints
    m.add_constr(mip.xsum(Y[i] for i in N) == p)

    for i in N:
        for j in N:
            m.add_constr(F[i][j] <= c[i] * X[i][j])

    for i in N:
        m.add_constr(mip.xsum(X[i][j] for j in N) <= 1)
        m.add_constr(mip.xsum(X[j][i] for j in N) <= 500 * Y[i])

    for j in N:
        m.add_constr(mip.xsum(F[i][j] for i in N) <= M / Q * Y[j])
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) <= kmax * mip.xsum(F[i][j] for i in N))
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) >= kmin * mip.xsum(F[i][j] for i in N))

    m.objective = mip.maximize(
        mip.xsum(F[i][j] * Q * b - dist[i, j] * X[i][j] for j in N for i in N))

    m.optimize()

    counter = 0
    for i in N:
        if Y[i].x > 1e-5:
            counter = counter + 1
    print_result(m, X, Y, F, N, points)

    last_value = m.objective_value
    while counter > p:
        if Y[0].x is None:
            return last_value
        else:
            last_value = m.objective_value
        min_val = 0
        removable = -1
        for j in N:
            if Y[j].x > 1e-5:
                for i in N:
                    cost = -1 * (dist[i, j] - F[i][j].x * Q * b)
                    if cost > min_val:
                        min_val = cost
                        removable = j
        m.add_constr(Y[removable] == 0)
        print(removable)
        m.optimize()
        for i in N:
            if Y[i].x > 1e-5:
                counter = counter + 1
        print_result(m, X, Y, F, N, points)
    return m.objective_value


def linear_relaxation2(data):
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

    X = [[m.add_var(lb=0, ub=1) for _ in N] for _ in N]
    Y = [m.add_var(lb=0, ub=1) for _ in N]
    F = [[m.add_var() for _ in N] for _ in N]

    # constraints
    m.add_constr(mip.xsum(Y[i] for i in N) == p)

    for i in N:
        for j in N:
            m.add_constr(F[i][j] <= c[i] * X[i][j])

    for i in N:
        m.add_constr(mip.xsum(X[i][j] for j in N) <= 1)
        m.add_constr(mip.xsum(X[j][i] for j in N) <= 500 * Y[i])

    for j in N:
        m.add_constr(mip.xsum(F[i][j] for i in N) <= M / Q * Y[j])
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) <= kmax * mip.xsum(F[i][j] for i in N))
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) >= kmin * mip.xsum(F[i][j] for i in N))

    m.objective = mip.maximize(
        mip.xsum(F[i][j] * Q * b - dist[i, j] * X[i][j] for j in N for i in N))

    m.optimize()
    print(m.objective_value)

    eps = 1e-5

    while True:
        m.optimize()
        pair = []  # Initialize pair to None, leave the loops

        for i in N:
            for j in N:
                # Check if inequality is violated (Add an epsilon to avoid numerical problems)
                if X[i][j].x > Y[j].x + eps:
                    pair.append({'x': i, 'y': j})
        if not len(pair):
            break

        while len(pair) > 0:
            elem = pair.pop()
            i = elem['x']
            j = elem['y']
            m.add_constr(X[i][j] <= Y[j])

    # print_result(m, X, Y, F, N, points)

    return m.objective_value


def distance_calc(points):
    N = range(len(points))
    return {(i, j): math.sqrt((points[i][0] - points[j][0]) ** 2 +
                              (points[i][1] - points[j][1]) ** 2)
            for i in N for j in N}


'''
    for i in N:
        print("farm", i, ":", end="\t")
        for j in N:
            print("{0:10.4f}".format(X[i][j].x), end="\t")
            print("\t")
        print()

    for i in N:
        print("farm", i, ":", end="\t")
        for j in N:
            print("{0:10.4f}".format(F[i][j].x), end="\t")
            print("\t")
        print()

    for i in N:
        print(Y[i].x)

    for i in N:
        print("farm", i, ":", end="\t")
        for j in N1:
            print("{0:10.4f}".format(X[i][j].x), end="\t")
            print("\t")
        print()
'''
