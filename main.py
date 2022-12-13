import mip
import math
import json


# Reads a .json instance and returns it in a dictionary
def load_instance(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


# Reads a .txt result and returns it
def load_result(filename):
    with open(filename, 'r') as f:
        result = f.read()
    return float(result)


def solve(instance):
    data = load_instance("instances/instance_4.json")

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
    dist = {(i, j): 1e-7 * math.sqrt((points[i][0] - points[j][0]) ** 2 +
                                     (points[i][1] - points[j][1]) ** 2)
            for i in N for j in N}
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
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) <= kmax * Y[j])
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) >= kmin * Y[j])

    m.objective = mip.maximize(
        mip.xsum(F[i][j] * Q * b - dist[i, j] * X[i][j] for j in N for i in N))
    m.optimize()
    print(m.objective_value)

    eps = 1e-5
    '''
    while True:
        m.optimize()
        pair = None  # Initialize pair to None, leave the loops
        for i in N:
            for j in N:
                # Check if inequality is violated (Add an epsilon to avoid numerical problems) TODO
                if X[i][j].x > Y[j].x + eps:
                    pair = (i, j)
                    break  # Leave the inner loop
            if pair is None:
                break  # Leave the outer loop if an inequality is found
        if pair is None:
            break  # No violated inequality was found, leave the loop
        i, j = pair
        m.add_constr(X[i][j] <= Y[j])
    
    for i in N:
        print("farm", i, ":", end="\t")
        for j in N:
            print("{0:10.4f}".format(X[i][j].x), end="\t")
            print("\t")
        print()
    '''

    for i in N:
        print(Y[i].x)
    '''
    for i in N:
        print("farm", i, ":", end="\t")
        for j in N1:
            print("{0:10.4f}".format(X[i][j].x), end="\t")
            print("\t")
        print()
    '''
    print_result(m, X, Y, N, points)

    return m.objective_value


def print_result(m, x, y, N, points):
    import networkx as nx
    import matplotlib.pyplot as plt

    print(f"Cost: {m.objective_value:.2f} M euro")

    print("Plants:")
    for j in N:
        if y[j].x > 1e-7:
            print(f"{j:3d} --> {y[j].x:7.3f}; farms: ", end='')
            for i in N:
                if x[i][j].x > 1e-7:
                    print(f"{i} ({x[i][j].x:.2f}); ", end='')
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


inst = load_instance("instances/instance_1.json")
res = load_result("instance_4.txt")

obj = solve(inst)

gap = 100 * (obj - res) / res

print("result: {}".format(obj))
print("expected: {}".format(res))
print("gap: {}".format(gap))
