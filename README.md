# Hướng dẫn cài thư viện trên python được sử dụng trong bài tập này
	## 1. Thư viện pulp
	Dùng trong Task 4 (ILP Deadlock) và Task 5 (ILP Optimization) để giải mô hình tối ưu hoá.
	Cách cài: 
		Gõ trên Terminal lệnh: "pip install pulp" để cài đặt

	## 2. Thư viện matplotlib
	Dùng trong Task 3 để:
	- Vẽ biểu đồ so sánh hiệu năng (BDD vs Explicit)
	- Lưu biểu đồ ra file .png
	Cách cài:
		Gõ trên Terminal lệnh: "pip install matplotlib" để cài đặt

	## 3. Thư viện psutil
	Dùng trong Task 3 để đo:
	- Lượng bộ nhớ tiêu thụ (memory usage)
	- Thông tin tiến trình
	Cách cài:
		Gõ trên Terminal lệnh: "pip install psutil" để cài đặt

# Symbolic and Algebraic Reasoning in Petri Nets
	Đây là Bài tập lớn của môn Mô hình hóa toán học (CO2011).
	Mục tiêu của bài tập:
	- Đọc và phân tích mô hình Petri Net từ file PNML
	- Sinh toàn bộ không gian reachable bằng:
		- Phương pháp tường minh Explicit BFS
		- Phương pháp tượng trưng Symbolic bằng Bitmask (BDD-like)
	- So sánh hiệu năng của 2 cách tiếp cận
	- Phát hiện Deadlock trên hệ thống
	- Giải bài toán tối ưu hóa ILP trên tập reachable markings

Bài làm gồm 5 task tương ứng với yêu cầu đề tài.
Tất cả code đều thuần Python, không dùng thư viện BDD ngoài (BDD được mô phỏng bằng bitmask).

Cấu trúc dự án gồm:
Assignment-CO2011-CSE251-{2413534-2413656-2413749-2414037-2414013}
task1.py        # Đọc file PNML, trích xuất Places / Transitions / Marking
task2.py        # Explicit BFS Reachability
task3.py        # Symbolic Reachability bằng Bitmask (BDD style)
task4.py        # Deadlock Detection
task5.py        # ILP Optimization
main.py         # File chạy toàn bộ các task
test1.pnml      # Các mô hình mẫu
test2.pnml
test3.pnml
test.xml		# File test mặc định 
README.md

# Cách chạy kiểm tra toàn bộ bài tập
	- Mở thư mục " " bằng VSCode
	- Gõ trên Temirnal lệnh "python main.py <tên file PNML>.pnml"
	    Một vài file PNML mẫu để kiểm tra gồm:
	    - test1
	    - test2
	    - test3
	Nếu không truyền file, chương trình mặc định dùng test.xml.

	File main.py thực hiện toàn bộ:
	- Task 1 → Đọc PNML
	- Task 2 → BFS Reachability
	- Task 3 → Symbolic BDD Reachability
	- Task 4 → Deadlock Detection
	- Task 5 → ILP Optimization

	Cuối cùng in ra:
	- Số trạng thái BFS
	- Số trạng thái BDD
	- Có deadlock hay không
	- Kết quả ILP
	- Thời gian thực thi

Dưới đây là toàn bộ các task được yêu cầu trong bài tập này
	
# Task 1 – Reading Petri nets from PNML files

	## 1. Mục tiêu
	- Đọc file PNML mô tả mô hình Petri net 
	- Trích xuất:
  		- Danh sách places
  		- Danh sách transitions
  		- Danh sách ARCS (pre-set và post-set)
  		- Initial marking
	- Kiểm tra tính nhất quán của PNML (no missing arcs or nodes)

	## 2. Cách chương trình hoạt động
	- Đọc places: 
		for placeNode in root.findall(".//{*}place"):
    	placeId = placeNode.get('id')
    	nameNode = placeNode.find(".//{*}text")

		Nếu có <name><text>...</text></name> → lấy tên
		Nếu không → dùng id làm tên mặc định
	- Đọc initial_marking:
		initMarkNode = placeNode.find(".//{*}initialMarking")

		Nếu <initialMarking><text>1</text></initialMarking> → place có token.
	- Đọc transitions: 
		for transNode in root.findall(".//{*}transition"):
            transId = transNode.get('id')
			name_node = transNode.find(".//{*}text")

		Nếu có <name><text>...</text></name> → lấy tên
		Nếu không → dùng id làm tên mặc định
	- Đọc Arcs:
		for arcNode in root.findall(".//{*}arc"):
            source = arcNode.get('source')
            target = arcNode.get('target')

    ## 3. Cách chạy
	- Mở thư mục " " bằng VSCode
	- Gõ trên Temirnal lệnh "py task1.py <tên file PNML>.pnml"
	    Một vài file PNML mẫu để kiểm tra gồm:
	    - test1
	    - test2
	    - test3

	## 4. Kết quả
	Chương trình sẽ hiển thị:
	- số lượng place
	- số lượng transition
	- initial marking ban đầu
	- lỗi nếu PNML không hợp lệ

# Task 2 - Explicit computation of reachable markings
	## 1. Mục tiêu
	- Task 2 hiện thực chức năng sinh toàn bộ không gian trạng thái (Reachability Graph) của một Petri Net bằng thuật toán BFS 	(Breadth-First Search).
	- Mỗi marking (trạng thái của Petri Net) được biểu diễn bằng tập các place có token.
	- Task 2 sử dụng PetriNet được tạo từ Task 1 (parser PNML) để:
		- Sinh tất cả các trạng thái reachable từ initial marking
		- Xác định quan hệ chuyển trạng thái qua transition
		- Phát hiện vòng lặp và tránh duyệt trùng
		- Chuẩn bị dữ liệu cho Task 4 (deadlock) và Task 3 (BDD)

	## 2. Thuật toán BFS
	- Khởi tạo
		m0 = frozenset(net.initial_marking)
		queue = deque([m0])
		visited = set([m0])
		edges = []
	- Vòng BFS
		while queue:
			m = queue.popleft()
	- Kiểm tra transition enable
		if inPlaces.issubset(m):
	- Sinh marking mới
		mAfter = set(m)
		mAfter.difference_update(inPlaces)
		mAfter.update(outPlaces)
		mAfter = frozenset(mAfter)
 	- Thêm vào queue nếu chưa từng thăm 
		if mAfter not in visited:
    			visited.add(mAfter)
    			queue.append(mAfter)

    ## 3. Cách chạy
	- Mở thư mục " " bằng VSCode
	- Gõ trên Temirnal lệnh "py task2.py <tên file PNML>.pnml"
		Một vài file PNML mẫu để kiểm tra gồm:
		- test1 
		- test2
		- test3

	## 4. Kết quả
	Chương trình sẽ hiển thị:
	- Tổng số trạng thái tìm thấy
	- Danh sách các trạng thái (Marking)
	nếu số trạng thái nhiều hơn 20 thì chương trình sẽ chỉ hiển thị 20 trạng thái đầu

# Task 3: Symbolic computation of reachable markings by using BDD

	## 1. Mục tiêu:
	- Giảm tiêu thụ bộ nhớ so với BFS explicit
	- Tăng tốc độ reachability với mạng lớn
	- Biểu diễn marking bằng số nguyên 64-bit (bitmask)
	- Ánh xạ “place → bit” => symbolic state
	- Tìm reachable states bằng fixpoint
	- So sánh hiệu năng explicit vs symbolic
	- Vẽ biểu đồ minh hoạ kết quả

	## 2. Cấu trúc:
	- BDDPetriNet: Khởi tạo BDD Petri Net từ đối tượng PetriNet (Task 1)
	- marking_to_bitmask(): Chuyển đổi marking thành bitmask số nguyên
	- bitmask_to_marking(): Chuyển đổi bitmask thành marking
	- is_enabled(): Kiểm tra transition có thể kích hoạt trong trạng thái hiện tại
	- fire_transition(): Thực hiện kích hoạt transition và trả về trạng thái mới
	- symbolic_reachability(): Thuật toán reachability tượng trưng sử dụng bitmask sets
	- compare_performance(): So sánh hiệu suất giữa phương pháp Explicit và Symbolic BDD
	- plot_comparison(): Vẽ biểu đồ

	## 3. Thuật toán Symbolic Reachability
	- Khởi tạo:
	R0 = { initial_marking_bitmask }
	- Vòng lặp fix point:
	while True:
    new_states = set()

    for bitmask in reachable:
        for trans_id in self.transitions:
            if self.is_enabled(bitmask, trans_id):
                new_bitmask = self.fire_transition(bitmask, trans_id)
                if new_bitmask not in reachable:
                    new_states.add(new_bitmask)

    reachable.update(new_states)
    if not new_states:
        break
	
	## 4. Tính hiệu năng
	Chương trình sẽ trả về:
	- Thời gian chạy
	- Số trạng thái
	- Số vòng lặp fix point
	- Bộ nhớ sử dụng
	- bitmask tối đa

	Ví dụ:
	Time: 0.004s
   	Bitmask States: 128
   	Markings: 128

	## 5. So sánh hiệu suất giữa Reachability explicit BFS và Reachability symbolic BDD
	Chương trình sẽ in ra bảng so sánh:
	- Thời gian thực thi 
	- Số trạng thái
	- Bộ nhớ sử dụng
	- Speedup
	Ví dụ:
	======================================================================
	Method             Time     States     Memory       Speedup
	----------------------------------------------------------------------
	Explicit BFS       0.007  s 128       6.2       KB
	Symbolic BDD       0.004  s 128       1.0       KB 1.67x
	✅ VERIFICATION PASSED: Both found 128 reachable markings

	## 6. Vẽ biểu đồ:
	Chương trình sinh ra file bdd_vs_explicit_comparison.png
	Biểu đồ so sánh gồm:
	- Thời gian hoàn thành
	- Số trạng thái
	- Bộ nhớ sử dụng
	- Hiệu quả sử dụng bộ nhớ

	## 7. Lưu kết quả
	Kết quả được lưu trong file reachability_results.pkl
	Bao gồm:
	- Cấu trúc mạng
	- Thông tin về explicit
	- Thông tin về BDD
	- So sánh hiệu suất

	## 8. Cách chạy
	- Mở thư mục " " bằng VSCode
	- Gõ trên Temirnal lệnh "py task3.py <tên file PNML>.pnml"
	    Một vài file PNML mẫu để kiểm tra gồm:
	    - test1
	    - test2
	    - test3

# Task 4: Deadlock detection by using ILP and BDD
	## 1. Mục tiêu
	- Phát hiện Deadlock trong mạng Petri bằng cách sử dụng:
		- Kết quả Reachability Symbolic (BDD) từ Task 3
		- Ràng buộc logic kiểm tra khả năng kích hoạt transition
	- Deadlock là trạng thái trong đó:
		- Không có bất kỳ transition nào còn enable
		- Hệ thống đứng yên vĩnh viễn, không tiến thêm được bước nào
	- Duyệt toàn bộ tập trạng thái reachable (đã được tính bằng BDD) và trả về:
		- Có tồn tại deadlock hay không
		- Nếu có thì trả về trạng thái gây deadlock
		- Thời gian kiểm tra

	## 2. Ý tưởng thuật toán
	- Sau khi Task 3 hoàn thành, bdd_net.reachable_states chứa đầy đủ marking biểu diễn dưới dạng BITMASK.
	- Bước 1: Lấy toàn bộ trạng thái reachable
	reachable_states = bdd_net.reachable_states
	- Bước 2: Duyệt từng trạng thái
	Với mỗi trạng thái (bitmask), kiểm tra: Transition nào enable?
	Hàm kiểm tra enable được tái sử dụng từ Task 3: bdd_net.is_enabled(mask, t_id)
	- Bước 3: Nếu không có transition enable → deadlock
	if not is_any_enabled:
    deadlock_found = True
    break
	- Bước 4: Giải mã bitmask thành marking
	bdd_net.bitmask_to_marking(deadlock_mask)

	## 3. Cách chạy
	- Mở thư mục " " bằng VSCode
	- Gõ trên Temirnal lệnh "py task4.py <tên file PNML>.pnml"
	    Một vài file PNML mẫu để kiểm tra gồm:
	    - test1
	    - test2
	    - test3

	## 4. Kết quả
	Chương trình sẽ hiển thị:
	- Có phát hiện deadlock hay không?
	- Thời gian thực thi
	- Nếu có deadlock thì hiển thị trạng thái gây deadlock

	Ví dụ:
	======================================================================
	💀 TASK 4: ILP + BDD DEADLOCK DETECTION
	======================================================================
	🔍 Đang kiểm tra ràng buộc Deadlock trên 1,946 trạng thái...
	❌ PHÁT HIỆN DEADLOCK!
   		⏱️  Thời gian: 0.0007s
   		📍 Tại trạng thái: ['p1', 'p_dead']

# Task 5: Optimization over reachable markings
	## 1. Mục tiêu:
	- Thực hiện bài toán tối ưu hóa trên không gian Reachable Markings của mạng Petri bằng cách:
		- Sử dụng kết quả BFS (Task 2) → tập Reach(M0)
		- Xây dựng bài toán Quy hoạch tuyến tính nguyên (ILP)
		- Tìm trạng thái (marking) có giá trị tối ưu nhất theo một vector trọng số
	- Mục tiêu tổng quát: Chọn đúng một marking trong Reach(M0) sao cho tổng trọng số của các place được đánh dấu là lớn nhất
	- Bài toán này thường được dùng để:
		- Tối ưu cấu hình hệ thống
		- Xác định trạng thái mong muốn nhất
		- Đánh giá hệ thống theo tiêu chí năng lượng, chi phí hoặc rủi ro

	## 2. Thuật toán
	- Ý tưởng ILP
		Cho Petri net với:
			Tập places: P={p1​,...,pn​}
			Tập reachable markings từ Task 2: M0, M1,..., Mk
		Ta muốn chọn đúng 1 marking có giá trị mục tiêu tối đa
	- Mô hình hóa ILP
		- Biến quyết định
		Biến marking: M[p] =
			- 1 nếu places p nằm trong marking được chọn
			- 0 ngược lại
		Biến chọn trạng thái: X[i] = 
			- 1 nếu marking Mi được chọn
			- 0 ngược lại
		- Ràng buộc
		Chọn đúng 1 trạng thái X[i] = 1
		Quan hệ giữa marking và place: M[p] = 1 nếu trạng thái được chọn có p
		- Hàm mục tiêu sum(c_p * M_p): tìm marking “tốt nhất” theo vector trọng số

	## 3. Cách chạy
	- Mở thư mục " " bằng VSCode
	- Gõ trên Temirnal lệnh "py task5.py <tên file PNML>.pnml"
	    Một vài file PNML mẫu để kiểm tra gồm gồm:
	    - test1
	    - test2
	    - test3

	## 4. Kết quả
	Chương trình sẽ in ra:
	- Số places, số transitions, số trạng thái
	- Vector trong số c
	- CBC MILP Solver...
	- Thời gian ILP
	- Giá trị tối ưu
	- Marking tối ưu
	- Trạng thái ILP chọn

	Ví dụ:
	Số places: 14
	Số transitions: 14
	Reach(M0) có 128 trạng thái

	Vector trọng số c:
	Switch_0_OFF : 14
	Switch_0_ON : 13
	...

	--- BẮT ĐẦU ILP ---
	CBC MILP Solver...
	Optimal solution found

	Giá trị tối ưu: 56

	Marking tối ưu gồm các place:
  	- Switch_0_OFF
  	- Switch_1_OFF
  	- Switch_2_OFF
  	- Switch_3_OFF
  	- Switch_4_OFF
  	- Switch_5_OFF
  	- Switch_6_OFF

	Trạng thái ILP chọn:
	['Switch_0_OFF', 'Switch_1_OFF', ..., 'Switch_6_OFF']
