import math
import Helper_functions


def min_cut(data):

    p = data["p"]
    Q = data["Q"]
    b = data["b"]
    m, Y, X, F, dist, points = Helper_functions.model_creation(data)
    N = range(len(Y))
    counter = 0
    for i in N:
        if Y[i].x > 1e-5:
            counter = counter + 1
    while counter > p:
        last_value = m.objective_value
        pairs = []

        for j in N:
            if Y[j].x > 1e-5:
                # consider total cost of plant -> gap decreases, but it looks like a nightmare and there are even more
                # double arcs
                cost = sum(F[i][j].x * Q * b - dist[i, j] for i in N if X[i][j].x > 1e-5)
                pairs.append({'y': j, 'cost': cost})
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
    m.optimize()
    Helper_functions.print_result(m, X, Y, F, N, points)

    return m.objective_value
