import json
import time
import Linear_Relaxation
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
    return MinCut.min_cut2(instance)


def write_results():
    out = open("results.csv", "w")
    out.write("ID, OBJ, TIME\n")
    for i in range(1, 11):
        inst = load_instance("instances/instance_{}.json".format(i))
        st = time.time()
        print("instance {}".format(i))
        res = solve(inst)
        et = time.time()
        out.write("{instance:},{value:},{time:}\n".format(instance=i, value=res, time=(et - st)))
    out.close()


#write_results()


inst = load_instance("instances/instance_1.json")
res = load_result("solutions/instance_1.txt")
st = time.time()

obj = solve(inst)

et = time.time()
print(et - st)

gap = 100 * (obj - res) / res

print("result: {}".format(obj))
print("expected: {}".format(res))
print("gap: {}".format(gap))
