import time as t
from task1 import PetriNet
from task2 import bfs
from pulp import *

def optimize_ILP(net, reachable, weights):
    print("\n--- BẮT ĐẦU ILP ---")
    start = t.time()
    states = list(reachable)
    places = list(net.places.keys())

    #1. Tạo bài toán max
    prob = LpProblem("OptMarking", LpMaximize)

    #2. Biến marking M[p] = 0/1
    M = {p: LpVariable(f"M_{p}", 0, 1, LpBinary) for p in places}

    #3. Biến chọn trạng thái x[i]
    X = {i: LpVariable(f"X_{i}", 0, 1, LpBinary) for i in range(len(states))}

    #4. Hàm mục tiêu: sum(c_p * M_p)
    prob += sum(weights.get(p, 0) * M[p] for p in places)

    #5. Chọn đúng 1 trạng thái
    prob += sum(X[i] for i in X) == 1

    #6. Ràng buộc: M[p] = 1 nếu trạng thái được chọn có p
    for p in places:
        prob += M[p] == sum(X[i] for i in X if p in states[i])

    #7. Giải
    prob.solve()
    end = t.time()
    print(f"Thời gian ILP: {end - start:.4f}s")

    if LpStatus[prob.status] != "Optimal":
        print("Không tìm thấy nghiệm tối ưu.")
        return

    #8. In kết quả
    val = value(prob.objective)
    print(f"\nGiá trị tối ưu: {val}")

    print("\nMarking tối ưu gồm các place:")
    result = []
    for p in places:
        if M[p].value() == 1:
            print("  -", net.places[p])
            result.append(p)

    #9. In trạng thái ứng với marking này
    for i in X:
        if X[i].value() == 1:
            names = [net.places[p] for p in states[i]]
            print("\nTrạng thái ILP chọn:", names)
            break


if __name__ == "__main__":
    import sys, os
    if len(sys.argv) < 2:
        print("Cách dùng: python task5.py <file_pnml>")
        exit()

    file = sys.argv[1]
    if not os.path.exists(file):
        print("Không tìm thấy file:", file)
        exit()

    net = PetriNet()
    if not net.read_PNML(file):
        print("Không đọc được PNML")
        exit()

    print("Số places:", len(net.places))
    print("Số transitions:", len(net.transitions))
    print("Initial marking:", list(net.initial_marking))

    reachable, edges = bfs(net)
    print("\nReach(M0) có", len(reachable), "trạng thái")

    # Tạo trọng số đơn giản: place sau có trọng số cao hơn
    weights = {}
    p_list = list(net.places.keys())
    for i, p in enumerate(p_list):
        weights[p] = len(p_list) - i
    print("\nVector trọng số c:")
    for p in weights:
        print(net.places[p], ":", weights[p])

    optimize_ILP(net, reachable, weights)
