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
    data = load_instance("instances/instance_1.json")

    M = data["M"]  # max energy production (kWh)
    Q = data["Q"]  # energy produced by a ton of corn chopping (kWh/t)
    a = data["a"]  # percentage of dry matter in chopping from farm i∈I
    b = data["b"]  # revenue per unit of energy (€/kWh)
    c = data["c"]  # tons of corn chopping available for each i∈I (t)
    kmax = data["kmax"]  # max percentage of dry matter for fermentation
    kmin = data["kmin"]  # min percentage of dry matter for fermentation
    n = int(data["n"])  # number of farms
    p = data["p"]  # number of plants to locate
    points = data["points"]  # coordinates of farm i∈I

    N = range(n)
    N1 = range(n)

    # TODO this could be done in a faster way
    dist = {(i, j): 1.0 * math.sqrt((points[i][0] - points[j][0]) ** 2 +
                                    (points[i][1] - points[j][1]) ** 2)
            for i in N for j in N}
    m = mip.Model()

    X = [[m.add_var(var_type=mip.BINARY) for _ in N1] for _ in N]
    Y = [m.add_var(var_type=mip.BINARY) for _ in N]
    F = [[m.add_var() for _ in N1] for _ in N]

    # constraints
    m.add_constr(mip.xsum(Y[i] for i in N) == p)

    for i in N:
        for j in N:
            m.add_constr(F[i][j] <= c[i] * X[i][j])

    for i in N:
        m.add_constr(mip.xsum(X[i][j] for j in N) == 1)

    for j in N:
        m.add_constr(mip.xsum(F[i][j] for i in N) <= M / Q * Y[j])
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) <= kmax * Y[j])
        m.add_constr(mip.xsum(a[i] * F[i][j] for i in N) >= kmin * Y[j])

    m.objective = mip.maximize(
        mip.xsum(F[i][j] * Q * b for j in N for i in N) -
        mip.xsum(dist[i, j] * X[i][j] for j in N for i in N))
    m.optimize()
    print(m.objective_value)

    for i in N:
        print("farm", i, ":", end="\t")
        for j in N1:
            print("{0:10.4f}".format(X[i][j].x), end="\t")
            print("\t")
        print()

    for i in N:
        print("farm", i, ":", end="\t")
        for j in N1:
            print("{0:10.4f}".format(F[i][j].x), end="\t")
            print("\t")
        print()

    for i in N:
        print(Y[i].x)

    return m.objective_value


inst = load_instance("instances/instance_1.json")
res = load_result("instance_1.txt")

obj = solve(inst)

gap = 100 * (obj - res) / res

print("result: {}".format(obj))
print("expected: {}".format(res))
print("gap: {}".format(gap))
