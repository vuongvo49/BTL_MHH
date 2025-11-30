import sys
import os
from collections import deque
from task1 import PetriNet
def bfs(net):
    # 1. Trạng thái ban đầu
    # fronzenset <-> const set
    m0 = frozenset(net.initial_marking)
    
    # 2. Khởi tạo 
    queue = deque([m0])
    visited = set([m0])
    edges = [] # Lưu trữ các cạnh (M1 -> t -> M2) 

    #3.Chạy bfs
    while queue:
        m = queue.popleft()            
        # Kiểm tra xem Transition nào fire
        for i in net.transitions:
            inPlaces = net.pre[i]
            outPlaces = net.post[i]
            
            # Enable condition
            # Nếu là tập con
            if inPlaces.issubset(m):
                # Token mới = (Cũ - Input) + Output
                mAfter = set(m)
                mAfter.difference_update(inPlaces) # Hiệu 2 tập hợp: Trừ token đi vào
                mAfter.update(outPlaces)           # Hợp 2 tập hợp: Cộng token đi ra
                mAfter = frozenset(mAfter) # Để lưu vào 1 set(visited) thì phần tử con phải là bất biến(const)

                edges.append((m, i, mAfter)) 

                # Nếu trạng thái này mới -> Thêm vào hàng đợi
                if mAfter not in visited:
                    visited.add(mAfter)
                    queue.append(mAfter)
    #Trả về danh sách đã thăm và danh sách cạnh
    return visited, edges

if __name__ == "__main__":
    filename = sys.argv[1]
    if os.path.exists(filename):
        Mynet = PetriNet()

        if Mynet.read_PNML(filename):
            visited_states, edges = bfs(Mynet) 
        
            # In kết quả
            print(f"Tổng số trạng thái tìm thấy: {len(visited_states)}")
            
            print("\nDanh sách các trạng thái (Markings):")
            for idx, state in enumerate(visited_states):
                # Lấy tên hiển thị(nếu k có tên thì sẽ là ID)
                names = [Mynet.places.get(p, p) for p in state]
                print(f"  State {idx}: {names}")
                
                if idx >= 19: #Nhiều quá thì in ra 20 cái
                    print(" ...")
                    break
    else:
        print(f"Lỗi: Không tìm thấy file '{filename}'")
