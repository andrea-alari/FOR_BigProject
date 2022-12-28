# this kind of algorithm doesn't work
import math

import mip

from helper_functions import distance_calc, print_result


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

    last_value = m.objective_value
    '''
    while True:
        if m.objective_value is None:
            return last_value
        else : last_value = m.objective_value
        for j in N:
            if Y[j].x > 0.5:
                m.add_constr(Y[j] == 0)
        m.optimize()

    pair = []
    counter = 0
    while counter < p:
        if m.objective_value is None:
            return last_value
        else: last_value = m.objective_value

        for i in N:
            for j in N:
                min_val = 0
                if X[i][j].x > 1e-5:
                    cost = -1 * (dist[i, j] * X[i][j].x - F[i][j].x * Q * b)
                    if cost > min_val:
                        min_val = cost
                        removable = {'x': i, 'y': j}
            pair.append(removable)

        while len(pair) > 0:
            elem = pair.pop()
            i = elem['x']
            j = elem['y']
            m.add_constr(X[i][j] == 0)
        m.optimize()
        counter = counter + 1


    '''
    counter = 0
    for i in N:
        if Y[i].x > 1e-5:
            counter = counter + 1
    # print_result(m, X, Y, F, N, points)
    while counter > p:
        last_value = m.objective_value
        min_val = 0
        removable = -1
        for j in N:
            if Y[j].x > 1e-5:
                # consider total cost of plant -> gap decreases, but it looks like a nightmare and there are even more
                # double arcs
                cost = mip.xsum(F[i][j].x * Q * b - dist[i, j] * X[i][j].x for i in N)
                if cost.x > min_val:
                    min_val = cost.x
                    removable = j
        m.add_constr(Y[removable] == 0)
        print(removable)
        m.optimize()
        if m.objective_value is None:
            return last_value
        for i in N:
            if Y[i].x > 1e-5:
                counter = counter + 1
        # print_result(m, X, Y, F, N, points)

    return m.objective_value


def min_cut2(data):
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

    last_value = m.objective_value

    counter = 0
    for i in N:
        if Y[i].x > 1e-5:
            counter = counter + 1
    # print_result(m, X, Y, F, N, points)
    while counter > p:
        last_value = m.objective_value
        pairs = []
        for j in N:
            if Y[j].x > 1e-5:
                # consider total cost of plant -> gap decreases, but it looks like a nightmare and there are even more
                # double arcs
                cost = mip.xsum(F[i][j].x * Q * b - dist[i, j] * X[i][j].x for i in N)
                pairs.append({'y': j, 'cost': cost.x})
        pairs.sort(key=lambda elem: elem['cost'])

        # removing first counter - p / 2 implants

        for i in range(math.ceil((counter - p) / 2)):
            m.add_constr(Y[pairs[i]['y']] == 0)

        m.optimize()
        if m.objective_value is None:
            return last_value
        counter = 0
        for i in N:
            if Y[i].x > 1e-5:
                counter = counter + 1
        # print_result(m, X, Y, F, N, points)
    '''   
    max = 0;
    for i in N:
        for j in N:
            if X[i][j].x > max:
                max = X[i][j].x
                ind = {'x': i, 'y': j}
            m.add_constr(X[ind['x']][ind['y']] == 1)
    m.optimize()
    print_result(m, X, Y, F, N, points)
    '''
    return m.objective_value
