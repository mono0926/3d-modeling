import cadquery as cq
import math

# --- パラメータ設定 ---
PITCH = 45.0          # キャップ中心間の距離（液ダレ干渉防止）
CAP_ID = 27.2         # Part A: ペグの直径（キャップの内側にスッと入るサイズ）
CAP_OD = 31.0         # Part B: ソケットの内径（キャップがスッポリ落ちるサイズ）
PEG_H = 10.0          # Part A: ペグの高さ
SOCKET_H = 10.0       # Part B: ソケットの深さ
BASE_THICK = 5.0      # ベースの厚み
HOLE_DIA = 12.0       # 押し出し・空気抜き用の貫通穴
ALIGN_DIA = 2.0       # 余ったフィラメント(1.75mm)を位置合わせダボにするための穴
HEX_R = 65.0          # 六角形ベースの外接円半径（ピタッと並べて拡張可能）

# 7つの座標（キャップ配置用）
cap_pts = [(0, 0)]
for i in range(6):
    angle = math.radians(60 * i)
    cap_pts.append((PITCH * math.cos(angle), PITCH * math.sin(angle)))

# 3つの座標（裏面の位置合わせダボ穴用：キャップの穴と干渉しない位置に配置）
align_pts = []
for i in range(3):
    angle = math.radians(120 * i + 30)
    align_pts.append((25.0 * math.cos(angle), 25.0 * math.sin(angle)))

# ==========================================
# Part A: 表面（上向き・アンブレラ用ペグ）
# ==========================================
part_a = (
    cq.Workplane("XY")
    .polygon(6, HEX_R * 2)
    .extrude(BASE_THICK)
    .faces(">Z").workplane()
    .pushPoints(cap_pts)
    .cylinder(PEG_H, CAP_ID / 2.0)
    .edges(">Z").chamfer(1.0) # キャップを被せやすくするための面取り
    .faces(">Z").workplane()
    .pushPoints(cap_pts)
    .hole(HOLE_DIA) # メンテナンス用貫通穴
    .faces("<Z").workplane()
    .pushPoints(align_pts)
    .hole(ALIGN_DIA, 3.0) # 裏面に深さ3mmのダボ穴
)

# ==========================================
# Part B: 裏面（下向き・ソケット受け皿）
# ==========================================
part_b = (
    cq.Workplane("XY")
    .polygon(6, HEX_R * 2)
    .extrude(BASE_THICK)
    .faces(">Z").workplane()
    .pushPoints(cap_pts)
    # リング状に出っ張らせる（厚さ3mmの壁）
    .circle(CAP_OD / 2.0 + 3.0).circle(CAP_OD / 2.0)
    .extrude(SOCKET_H)
    .faces(">Z").workplane()
    .pushPoints(cap_pts)
    .hole(HOLE_DIA) # メンテナンス用貫通穴
    .faces("<Z").workplane()
    .pushPoints(align_pts)
    .hole(ALIGN_DIA, 3.0) # 裏面に深さ3mmのダボ穴
)

# --- 出力用 ---
# CQ-editor等で確認する場合は表示
# show_object(part_a, name="Part_A")
# show_object(part_b, name="Part_B")

# STL出力（実行時にコメントアウトを外してください）
cq.exporters.export(part_a, "Part_A_Pegs.step")
cq.exporters.export(part_b, "Part_B_Sockets.step")
