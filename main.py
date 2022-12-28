import json
import time
import Solutions
import MinCut


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
    st = time.time()
    res = MinCut.min_cut2(instance)
    et = time.time()
    print(et -st)
    return res


def write_results():
    out = open("results.csv", "w")
    out.write("ID, OBJ, TIME\n")
    for i in range(1, 11):
        inst = load_instance("instances/instance_{}.json".format(i))
        st = time.time()
        res = solve(inst)
        et = time.time()
        out.write("{instance:},{value:},{time:}\n".format(instance=i, value=res, time=(et - st)))
    out.close()


#write_results()
inst = load_instance("instances/instance_4.json")
res = load_result("solutions/instance_4.txt")

obj = solve(inst)

gap = 100 * (obj - res) / res

print("result: {}".format(obj))
print("expected: {}".format(res))
print("gap: {}".format(gap))
