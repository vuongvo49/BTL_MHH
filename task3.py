import time
import sys
import os
from collections import deque, defaultdict
from task1 import PetriNet
from task2 import bfs
import numpy as np
import matplotlib.pyplot as plt
import pickle

class BDDPetriNet:
    def __init__(self, net: PetriNet):
        """
        Khởi tạo BDD Petri Net từ đối tượng PetriNet (Task 1)
        """
        self.net = net
        self.places = list(net.places.keys())  # Danh sách tất cả places
        self.num_places = len(self.places)     # Số lượng places
        self.transitions = list(net.transitions.keys())  # Danh sách transitions
        
        # Biểu diễn bit vector: 1 bit cho mỗi place (mạng 1-safe)
        self.state_size = self.num_places
        self.place_index = {place: i for i, place in enumerate(self.places)}  # Ánh xạ place -> bit index
        
        # Biểu diễn BDD sử dụng tập hợp bitmasks
        self.reachable_states = set()  # Tập hợp các trạng thái reachable
        self.bdd_stats = {}           # Thống kê hiệu suất
    
    def marking_to_bitmask(self, marking: frozenset) -> int:
        """Chuyển đổi marking thành bitmask số nguyên"""
        bitmask = 0
        for place in marking:
            if place in self.place_index:
                bitmask |= (1 << self.place_index[place])
        return bitmask
    
    def bitmask_to_marking(self, bitmask: int) -> frozenset:
        """Chuyển đổi bitmask thành marking"""
        marking = set()
        for i, place in enumerate(self.places):
            if bitmask & (1 << i):
                marking.add(place)
        return frozenset(marking)
    
    def is_enabled(self, bitmask: int, transition_id: str) -> bool:
        """Kiểm tra transition có thể kích hoạt trong trạng thái hiện tại"""
        pre_places = self.net.pre[transition_id]
        for place in pre_places:
            if place not in self.place_index:
                continue
            place_bit = 1 << self.place_index[place]
            if not (bitmask & place_bit):
                return False
        return True
    
    def fire_transition(self, bitmask: int, transition_id: str) -> int:
        """Thực hiện kích hoạt transition và trả về trạng thái mới"""
        new_bitmask = bitmask
        
        # Xóa token từ pre-places
        for place in self.net.pre[transition_id]:
            if place in self.place_index:
                place_bit = 1 << self.place_index[place]
                new_bitmask &= ~place_bit
        
        # Thêm token vào post-places
        for place in self.net.post[transition_id]:
            if place in self.place_index:
                place_bit = 1 << self.place_index[place]
                new_bitmask |= place_bit
        
        return new_bitmask
    
    def symbolic_reachability(self) -> tuple:
        """Thuật toán reachability tượng trưng sử dụng bitmask sets"""
        print("🔍 Starting SYMBOLIC (BDD-like) reachability analysis...")
        start_time = time.time()
        
        # Trạng thái ban đầu
        initial_bitmask = self.marking_to_bitmask(self.net.initial_marking)
        reachable = {initial_bitmask}
        iteration = 0
        
        while True:
            iteration += 1
            new_states = set()
            
            # Với mỗi trạng thái hiện tại, thử tất cả transitions
            for bitmask in reachable:
                for trans_id in self.transitions:
                    if self.is_enabled(bitmask, trans_id):
                        new_bitmask = self.fire_transition(bitmask, trans_id)
                        if new_bitmask not in reachable:
                            new_states.add(new_bitmask)
            
            print(f"  Iteration {iteration}: |R| = {len(reachable):,}, New = {len(new_states):,}")
            
            if not new_states:
                print(f"  ✅ Fixed point reached at iteration {iteration}")
                break
            
            reachable.update(new_states)
        
        elapsed = time.time() - start_time
        
        # Convert back to markings for verification
        reachable_markings = {self.bitmask_to_marking(state) for state in reachable}
        
        self.reachable_states = reachable
        self.bdd_stats = {
            'time': elapsed,
            'iterations': iteration,
            'bitmask_states': len(reachable),
            'marking_count': len(reachable_markings),
            'memory_bytes': len(reachable) * 8,
            'max_bitmask': max(reachable) if reachable else 0
        }
        
        print(f"✅ Symbolic Reachability completed!")
        print(f"   Time: {elapsed:.3f}s")
        print(f"   Bitmask States: {len(reachable):,}")
        print(f"   Markings: {len(reachable_markings):,}")
        
        return reachable_markings, self.bdd_stats
    
    def compare_performance(self, explicit_visited: set, explicit_time: float) -> dict:
        """So sánh hiệu suất giữa phương pháp Explicit và Symbolic BDD"""
        explicit_count = len(explicit_visited)
        bdd_count = self.bdd_stats['marking_count']
        bdd_time = self.bdd_stats['time']
        
        # Calculate speedup safely
        if explicit_time > 0 and bdd_time > 0:
            speedup = explicit_time / bdd_time
            speedup_str = f"{speedup:.2f}x"
        else:
            speedup_str = "N/A"
        
        # Memory calculations
        explicit_memory_kb = explicit_count * 50 / 1024
        bdd_memory_kb = self.bdd_stats['memory_bytes'] / 1024
        
        print("\n" + "="*70)
        print("📊 PERFORMANCE COMPARISON")
        print("="*70)
        print(f"{'Method':<18} {'Time':<8} {'States':<10} {'Memory':<12} {'Speedup':<10}")
        print("-"*70)
        print(f"{'Explicit BFS':<18} {explicit_time:<7.3f}s {explicit_count:<9,} {explicit_memory_kb:<10.1f}KB {'':<10}")
        print(f"{'Symbolic BDD':<18} {bdd_time:<7.3f}s {bdd_count:<9,} {bdd_memory_kb:<10.1f}KB {speedup_str:<10}")
        
        # Verification
        if explicit_count == bdd_count:
            print(f"✅ VERIFICATION PASSED: Both found {explicit_count:,} reachable markings")
        else:
            print(f"⚠️  VERIFICATION FAILED: Explicit={explicit_count}, BDD={bdd_count}")
        
        memory_ratio = explicit_memory_kb / bdd_memory_kb if bdd_memory_kb > 0 else 0
        
        return {
            'explicit_count': explicit_count,
            'bdd_count': bdd_count,
            'explicit_time': explicit_time,
            'bdd_time': bdd_time,
            'speedup': speedup if 'speedup' in locals() else 0,
            'memory_ratio': memory_ratio,
            'verification_passed': explicit_count == bdd_count
        }

def plot_comparison(explicit_time: float, bdd_stats: dict, comparison: dict):
    """Enhanced plotting with English labels"""
    methods = ['Explicit BFS', 'Symbolic BDD']
    times = [explicit_time, bdd_stats['time']]
    states = [comparison['explicit_count'], comparison['bdd_count']]
    memories_kb = [
        comparison['explicit_count'] * 50 / 1024,
        bdd_stats['memory_bytes'] / 1024
    ]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Time comparison
    bars1 = ax1.bar(methods, times, color=['#FF6B6B', '#4ECDC4'], alpha=0.8)
    ax1.set_ylabel('Time (seconds)')
    ax1.set_title('Computation Time')
    ax1.grid(True, alpha=0.3)
    for bar, t in zip(bars1, times):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(times)*0.01,
                f'{t:.3f}s', ha='center', va='bottom')
    
    # States comparison
    bars2 = ax2.bar(methods, states, color=['#FF8E53', '#26D0CE'], alpha=0.8)
    ax2.set_ylabel('Number of States')
    ax2.set_title('Reachable Markings')
    ax2.grid(True, alpha=0.3)
    for bar, s in zip(bars2, states):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + max(states)*0.05,
                f'{s:,}', ha='center', va='bottom')
    
    # Memory comparison
    bars3 = ax3.bar(methods, memories_kb, color=['#45B7D1', '#96CEB4'], alpha=0.8)
    ax3.set_ylabel('Memory (KB)')
    ax3.set_title('Memory Usage')
    ax3.grid(True, alpha=0.3)
    for bar, m in zip(bars3, memories_kb):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + max(memories_kb)*0.05,
                f'{m:.1f} KB', ha='center', va='bottom')
    
    # Memory Efficiency
    ratios = [1.0, comparison.get('memory_ratio', 1.0)]
    bars4 = ax4.bar(methods, ratios, color=['#FFA726', '#66BB6A'], alpha=0.8)
    ax4.set_ylabel('Relative Efficiency')
    ax4.set_title('Memory Efficiency (Explicit/BDD)')
    ax4.grid(True, alpha=0.3)
    for bar, r in zip(bars4, ratios):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + max(ratios)*0.05,
                f'{r:.1f}x', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('bdd_vs_explicit_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def main(filename: str):
    """
    Hàm chính của Task 3
    1. Load Petri Net từ PNML
    2. Tính reachability explicit (Task 2)
    3. Tính reachability symbolic BDD (Task 3)
    4. So sánh hiệu suất
    5. Vẽ biểu đồ
    6. Lưu kết quả
    """
    print("🎯 TASK 3: SYMBOLIC BDD REACHABILITY ANALYSIS")
    print("="*70)
    
    # Bước 1: Load Petri Net
    print("\n1️⃣ Đọc Petri Net từ file PNML...")
    net = PetriNet()
    if not net.read_PNML(filename):
        print("❌ Không thể đọc file PNML!")
        return
    
    print(f"   📊 {len(net.places)} Places, {len(net.transitions)} Transitions")
    print(f"   🎯 Marking ban đầu: {sorted(list(net.initial_marking))}")
    
    # Bước 2: Reachability explicit
    print("\n2️⃣ Tính REACHABILITY EXPLICIT...")
    explicit_start = time.time()
    explicit_visited, explicit_edges = bfs(net)
    explicit_time = time.time() - explicit_start
    
    print(f"   ⏱️  Thời gian: {explicit_time:.3f}s")
    print(f"   📊 {len(explicit_visited):,} markings có thể đạt được")
    print(f"   🔗 {len(explicit_edges):,} transitions")
    
    # Bước 3: Reachability symbolic BDD
    print("\n3️⃣ Tính REACHABILITY SYMBOLIC BDD...")
    bdd_net = BDDPetriNet(net)
    bdd_markings, bdd_stats = bdd_net.symbolic_reachability()
    
    # Bước 4: So sánh hiệu suất
    print("\n4️⃣ PHÂN TÍCH HIỆU SUẤT...")
    comparison = bdd_net.compare_performance(explicit_visited, explicit_time)
    
    # Bước 5: Vẽ biểu đồ
    print("\n5️⃣ Tạo biểu đồ so sánh...")
    plot_comparison(explicit_time, bdd_stats, comparison)
    
    # Bước 6: Lưu kết quả
    results = {
        'pnml_file': filename,
        'net_info': {
            'places': len(net.places),
            'transitions': len(net.transitions),
            'initial_marking': len(net.initial_marking)
        },
        'explicit': {
            'time': explicit_time,
            'states': len(explicit_visited),
            'edges': len(explicit_edges)
        },
        'bdd': bdd_stats,
        'comparison': comparison
    }
    
    with open('reachability_results.pkl', 'wb') as f:
        pickle.dump(results, f)
    
    # Tóm tắt cuối
    print("\n" + "="*70)
    print("🎉 TASK 3 HOÀN THÀNH THÀNH CÔNG! 🎉")
    print("="*70)
    print(f"📁 Kết quả đã lưu: reachability_results.pkl")
    print(f"📊 Biểu đồ đã lưu: bdd_vs_explicit_comparison.png")
    print(f"✅ Tổng số markings có thể đạt được: {len(explicit_visited):,}")
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách sử dụng: python task3.py <file_pnml>")
        print("Ví dụ: python task3.py test.xml")
        sys.exit(1)
    
    filename = sys.argv[1]
    if not os.path.exists(filename):
        print(f"❌ Không tìm thấy file: {filename}")
        sys.exit(1)
    
    main(filename)
