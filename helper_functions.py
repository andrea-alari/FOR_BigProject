import networkx as nx
import matplotlib.pyplot as plt


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
