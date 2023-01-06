import json
import time
import ThinModel


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
    return ThinModel.thin_model(instance)


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


# write_results()

inst = load_instance("instances/instance_1.json")
st = time.time()
obj = solve(inst)
print("--- RESULT ---")
print("result(€) : {0:10.2f}".format(obj))
print("time(s) : {0:10.5f}".format(time.time() - st))
res = load_result("solutions/instance_1.txt")
gap = 100 * (obj - res) / res
print("gap: {}".format(gap))
print("expected: {}".format(res))

