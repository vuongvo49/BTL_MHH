import time
from task3 import BDDPetriNet

def check_deadlock_constraints(bdd_net: BDDPetriNet):
    """
    TASK 4: Kiểm tra Deadlock bằng cách duyệt qua các trạng thái Reachable
    đã được tính toán ở Task 3.
    """
    print("\n" + "="*70)
    print("💀 TASK 4: ILP + BDD DEADLOCK DETECTION")
    print("="*70)

    start_time = time.time()
    
    # Lấy tập hợp các trạng thái Reachable (đã được mã hóa thành số nguyên bitmask)
    # Nếu code báo lỗi ở dòng này, hãy đảm bảo task3.py đã chạy xong symbolic_reachability
    try:
        reachable_states = bdd_net.reachable_states
    except AttributeError:
        print("⚠️  LỖI: Không tìm thấy biến reachable_states trong bdd_net.")
        return False, None
    
    if not reachable_states:
        print("⚠️  Cảnh báo: Tập Reachable rỗng. Hãy kiểm tra lại Task 3.")
        return False, None

    print(f"🔍 Đang kiểm tra ràng buộc Deadlock trên {len(reachable_states):,} trạng thái...")
    
    deadlock_mask = None
    deadlock_found = False

    # DUYỆT QUA TỪNG TRẠNG THÁI (MARKING)
    for mask in reachable_states:
        is_any_enabled = False
        
        # Kiểm tra: Tại trạng thái 'mask', có transition nào bắn được không?
        for t_id in bdd_net.transitions:
            # Tận dụng hàm kiểm tra logic có sẵn của Task 3
            if bdd_net.is_enabled(mask, t_id):
                is_any_enabled = True
                break # Nếu có transition chạy được -> Trạng thái này AN TOÀN -> Next
        
        # Nếu duyệt hết transition mà không cái nào chạy được -> DEADLOCK
        if not is_any_enabled:
            deadlock_mask = mask
            deadlock_found = True
            break 

    elapsed = time.time() - start_time
    
    # KẾT QUẢ
    if deadlock_found:
        # Giải mã từ số nguyên bitmask sang tên Place để in ra
        deadlock_marking = bdd_net.bitmask_to_marking(deadlock_mask)
        print(f"❌ PHÁT HIỆN DEADLOCK!")
        print(f"   ⏱️  Thời gian: {elapsed:.4f}s")
        print(f"   📍 Tại trạng thái: {list(deadlock_marking)}")
        return True, deadlock_marking
    else:
        print(f"✅ KHÔNG CÓ DEADLOCK.")
        print(f"   ⏱️  Thời gian: {elapsed:.4f}s")
        return False, None


        # main
import sys
from task1 import PetriNet

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python task4.py <tên_file_pnml>")
        # Mặc định thử với test.xml nếu không nhập gì
        filename = "test.xml"
    else:
        filename = sys.argv[1]

    import os
    if os.path.exists(filename):
        print(f"🚀 [Standalone Mode] Đang test riêng Task 4 với file: {filename}")
        
        # 1. Task 1 để đọc file
        net = PetriNet()
        net.read_PNML(filename)
        
        # 2. Task 3 để có Reachability
        bdd_net = BDDPetriNet(net)
        print(">> Đang chạy Reachability (Task 3)...")
        bdd_net.symbolic_reachability()
        
        # 3. Chạy hàm 
        check_deadlock_constraints(bdd_net)
    else:
        print(f"❌ Không tìm thấy file: {filename}")
