import xml.etree.ElementTree as ET
import sys
import os
from collections import deque


class PetriNet:
    def __init__(self):
        self.places = {}         
        self.transitions = {}   
        self.pre = {}           # Điểm đầu
        self.post = {}          # Điểm đích
        self.initial_marking = set() #Các điểm được đánh dấu ban đầu
# ==========================================
# TASK 1
# ==========================================
    def read_PNML(self, filepath):
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
        except Exception as e:
            print(f"LỖI: Không thể mở file")
            return False

        # --- 1. TÌM PLACES (VỊ TRÍ) ---
        for placeNode in root.findall(".//{*}place"):
            placeId = placeNode.get('id')
            if not placeId: continue # Skip nếu không có ID

            # Lấy tên (Name)
            petriName = placeId # Nếu k có name thì name sẽ là id
            nameNode = placeNode.find(".//{*}text") # Tìm thẻ text bên trong name
            if nameNode is not None and nameNode.text:
                petriName = nameNode.text.strip() #strip() để chuẩn hóa chuỗi
            
            self.places[placeId] = petriName

            # Lấy Trạng thái ban đầu
            # Tìm thẻ initialMarking, sau đó tìm thẻ text bên trong nó
            initMarkNode = placeNode.find(".//{*}initialMarking")
            
            if initMarkNode is not None:
                textNode = initMarkNode.find(".//{*}text")
                
                val_str = "0"
                if textNode is not None and textNode.text:
                    val_str = textNode.text.strip()
                elif initMarkNode.text:
                    val_str = initMarkNode.text.strip()

                try:
                    if int(val_str) > 0:
                        self.initial_marking.add(placeId)
                except ValueError: 
                    pass

        # --- 2. TÌM TRANSITIONS  ---
        for transNode in root.findall(".//{*}transition"):
            transId = transNode.get('id')
            if not transId: continue

            # Lấy tên
            transName = transId
            name_node = transNode.find(".//{*}text")
            if name_node is not None and name_node.text:
                transName = name_node.text.strip()

            self.transitions[transId] = transName
            
            # Khởi tạo danh sách cung
            self.pre[transId] = set()
            self.post[transId] = set()

        # --- 3. TÌM ARCS---
        for arcNode in root.findall(".//{*}arc"):
            source = arcNode.get('source')
            target = arcNode.get('target')

            if not source or not target:
                continue

            if source in self.places and target in self.transitions:
                # Place -> Transition (Pre)
                self.pre[target].add(source)
            elif source in self.transitions and target in self.places:
                # Transition -> Place (Post)
                self.post[source].add(target)
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        net = PetriNet()
        net.read_PNML(sys.argv[1])
        print(f"-> Đã tìm thấy: {len(net.places)} Places, {len(net.transitions)} Transitions")
        print(f"-> Initial Marking (Token ban đầu tại): {list(net.initial_marking)}")
