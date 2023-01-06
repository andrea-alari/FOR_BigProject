import math

import mip

from Helper_functions import distance_calc


class Plant:
    def __init__(self, index, possibleConnections, Y):
        self.index = index
        self.possibleConnections = possibleConnections
        self.Y = Y
        self.X = []
        self.F = []


class Farm:
    def __init__(self, index):
        self.index = index
        self.X = []
        self.F = []


def thin_model(data):
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
    prod = M / Q

    m = mip.Model()
    m.verbose = 0

    # we are saving only the closest farm to each implant
    plants = [Plant(i, [], m.add_var(lb=0, ub=1)) for i in N]
    farms = [Farm(i) for i in N]
    if n * 4 / p > n:
        cluster = n
    else:
        cluster = math.ceil(n * 4 / p)
    for i in N:
        pairs = []
        for j in N:
            pairs.append({'j': j, 'dist': dist[i, j]})
        pairs.sort(key=lambda elem: elem['dist'])

        for j in range(cluster):
            plants[i].possibleConnections.append(pairs[j]["j"])

    # constraints

    m.add_constr(mip.xsum(plant.Y for plant in plants) == p)
    for i in N:
        for j in plants[i].possibleConnections:
            x_var = m.add_var(lb=0, ub=1)
            f_var = m.add_var()
            farms[j].X.append({'x': x_var, 'i': i})
            farms[j].F.append(f_var)
            plants[i].X.append(x_var)
            plants[i].F.append({'f': f_var, 'j': j})

    for i in N:
        farm = farms[i]
        for j in range(len(farm.X)):
            m.add_constr(farm.F[j] <= c[i] * farm.X[j]['x'])
        m.add_constr(mip.xsum(i['x'] for i in farm.X) <= 1)

    for plant in plants:
        m.add_constr(mip.xsum(i for i in plant.X) <= cluster * plant.Y)
        m.add_constr(mip.xsum(i['f'] for i in plant.F) <= prod)
        m.add_constr(mip.xsum(a[i['j']] * i['f'] for i in plant.F) <= kmax * mip.xsum(i['f'] for i in plant.F))
        m.add_constr(mip.xsum(a[i['j']] * i['f'] for i in plant.F) >= kmin * mip.xsum(i['f'] for i in plant.F))

    m.objective = mip.maximize(
        mip.xsum(
            plant.F[i]['f'] * Q * b - dist[plant.index, plant.F[i]['j']] * plant.X[i] for i in range(len(plant.F)) for
            plant in plants))

    m.optimize()
    counter = 0
    for plant in plants:
        if plant.Y.x > 1e-5:
            counter = counter + 1

    while counter > p:
        last_value = m.objective_value
        pairs = []

        for plant in plants:
            if plant.Y.x > 1e-5:
                # consider total cost of plant -> gap decreases, but it looks like a nightmare and there are even more
                # double arcs
                cost = sum(plant.F[i]['f'].x * Q * b - dist[plant.index, plant.F[i]['j']] * plant.X[i].x for i in
                           range(len(plant.F)) if plant.X[i].x > 1e-5)
                pairs.append({'plant': plant, 'cost': cost})
        pairs.sort(key=lambda elem: elem['cost'])

        # removing first counter - p / 2 implants
        for i in range(math.ceil((counter - p) / 2)):
            m.add_constr(pairs[i]['plant'].Y == 0)

        m.optimize()
        if m.objective_value is None:
            return last_value
        counter = 0
        for plant in plants:
            if plant.Y.x > 1e-5:
                counter = counter + 1

    return m.objective_value
