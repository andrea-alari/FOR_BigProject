import math
import mip
import networkx as nx
import matplotlib.pyplot as plt


def model_creation(data):
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

    dist = distance_calc(points)

    m = mip.Model()

    X = [[m.add_var(lb=0, ub=1) for _ in N] for _ in N]
    Y = [m.add_var(lb=0, ub=1) for _ in N]
    F = [[m.add_var() for _ in N] for _ in N]

    # constraints
    m.add_constr(mip.xsum(Y[i] for i in N) == p)

    maxFarms = []

    for i in N:
        count = 0
        for j in N:
            if c[j] < M / Q:
                if dist[i, j] < c[j] * Q * b:
                    count = count + 1
            else:
                if dist[i, j] < M * b:
                    count = count + 1
                else:
                    m.add_constr(X[j][i] == 0)
        maxFarms.append(count)
    for i in N:
        for j in N:
            m.add_constr(F[i][j] <= c[i] * X[i][j])

    for i in N:
        m.add_constr(mip.xsum(X[i][j] for j in N) <= 1)
        m.add_constr(mip.xsum(X[j][i] for j in N) <= maxFarms[i] * Y[i])

    for j in N:
        m.add_constr(mip.xsum(F[i][j] for i in N) <= M / Q)
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) <= kmax * mip.xsum(F[i][j] for i in N))
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) >= kmin * mip.xsum(F[i][j] for i in N))

    m.objective = mip.maximize(
        mip.xsum(F[i][j] * Q * b - dist[i, j] * X[i][j] for j in N for i in N))

    m.verbose = 0
    return m, Y, X, F, dist, points


def print_result(m, x, y, f, N, points):
    print(f"Cost: {m.objective_value:.2f} M euro")

    print("Plants:")
    for j in N:
        if y[j].x > 1e-7:
            print(f"{j:3d} --> {y[j].x:7.3f}; farms: ", end='')
            for i in N:
                if x[i][j].x > 1e-7:
                    print(f"{i} ({x[i][j].x:.2f}) ({f[i][j].x:.2f}); ", end='')
            print('')
    # Visualize solution on graph
    pos_a = {f'F{i}': (points[i][0], points[i][1]) for i in N}

    nodes = {**pos_a}

    g = nx.Graph()
    g.add_nodes_from([f'F{j}' for j in N])
    g.add_nodes_from([f'F{i}' for i in N])
    edges = [(f'F{i}', f'F{j}') for j in N for i in N if x[i][j].x > 0]
    g.add_edges_from(edges)
    plt.figure(1, figsize=(14, 14))
    nx.draw_networkx(g, font_size=11, pos=nodes)
    plt.show()


def distance_calc(points):
    N = range(len(points))
    return {(i, j): math.sqrt((points[i][0] - points[j][0]) ** 2 +
                              (points[i][1] - points[j][1]) ** 2)
            for i in N for j in N}
