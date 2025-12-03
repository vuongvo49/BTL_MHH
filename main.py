import sys
import os
from task1 import PetriNet
from task2 import bfs
from task3 import BDDPetriNet
from task4 import check_deadlock_constraints
from task5 import optimize_ILP

def main():
    # -------------------------------
    # 0. Kiểm tra tham số đầu vào
    # -------------------------------
    if len(sys.argv) < 2:
        print("⚠️  Cách dùng: python main.py <tên_file_pnml>")
        print("➡️  Không nhập file → dùng mặc định: test.xml")
        filename = "test.xml"
    else:
        filename = sys.argv[1]

    if not os.path.exists(filename):
        print(f"❌ Lỗi: Không tìm thấy file '{filename}'")
        return

    print("====================================================================")
    print(f"🚀 BẮT ĐẦU CHẠY TOÀN BỘ BTL VỚI FILE: {filename}")
    print("====================================================================\n")

    # -------------------------------
    # Task 1: Đọc PNML
    # -------------------------------
    print("=== [TASK 1] ĐỌC FILE PNML ===")
    net = PetriNet()
    if not net.read_PNML(filename):
        print("❌ Không thể đọc PNML. Dừng chương trình.")
        return
    print(f"✔ Số places: {len(net.places)}")
    print(f"✔ Số transitions: {len(net.transitions)}")
    print(f"✔ Initial marking: {list(net.initial_marking)}\n")

    # -------------------------------
    # Task 2: Explicit BFS
    # -------------------------------
    print("=== [TASK 2] EXPLICIT BFS REACHABILITY ===")
    reachable, edges = bfs(net)
    print(f"✔ Reach(M0) có {len(reachable)} trạng thái\n")

    # -------------------------------
    # Task 3: Symbolic BDD
    # -------------------------------
    print("=== [TASK 3] SYMBOLIC BDD REACHABILITY ===")
    bdd_net = BDDPetriNet(net)
    bdd_net.symbolic_reachability()  
    print(f"✔ Symbolic Reachability tìm thấy {len(bdd_net.reachable_states)} trạng thái\n")

    # -------------------------------
    # Task 4: Deadlock Detection
    # -------------------------------
    print("=== [TASK 4] DEADLOCK DETECTION (BDD) ===")
    check_deadlock_constraints(bdd_net)
    print()

    # -------------------------------
    # Task 5: ILP Optimization
    # -------------------------------
    print("=== [TASK 5] ILP OPTIMIZATION ===")

    # Tạo vector trọng số mẫu: place cuối có trọng số nhỏ
    weights = {}
    p_list = list(net.places.keys())
    for i, p in enumerate(p_list):
        weights[p] = len(p_list) - i

    print("Vector trọng số c:")
    for p in weights:
        print(f"  {net.places[p]} : {weights[p]}")
    print()

    optimize_ILP(net, reachable, weights)

    print("\n====================================================================")
    print("🎉 HOÀN THÀNH TOÀN BỘ 5 TASK!")
    print("====================================================================")


if __name__ == "__main__":
    main()

