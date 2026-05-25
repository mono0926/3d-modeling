import cadquery as cq
import os

# ==================== パラメータ定義 ====================
BASE_THICKNESS = 2.0   # ベースプレートの厚さ
INSERT_DEPTH = 4.4     # ユーザー測定の差し込み口の深さ
TOTAL_HEIGHT = BASE_THICKNESS + INSERT_DEPTH # 円柱全体の高さ (6.4mm)
SOCKET_WALL = 2.1      # 本番ノズルと同一の肉厚
PLATE_WIDTH = 80.0
PLATE_DEPTH = 45.0

def create_hollow_cylinder(diameter):
    r_outer = diameter / 2.0
    r_inner = (diameter - 2.0 * SOCKET_WALL) / 2.0
    
    # 1. 外側円筒 (centered=True で作ってからZ方向に移動)
    outer = cq.Workplane("XY").cylinder(height=TOTAL_HEIGHT, radius=r_outer, centered=(True, True, True))
    outer = outer.translate((0, 0, TOTAL_HEIGHT / 2.0))
    
    # 導入用の面取り (外径上端)
    outer = outer.edges(">Z").chamfer(0.5)
    
    # 2. 内側穴 (Z=0 から TOTAL_HEIGHT まで貫通カットするために少し長めに作成)
    inner = cq.Workplane("XY").cylinder(height=TOTAL_HEIGHT + 0.2, radius=r_inner, centered=(True, True, True))
    inner = inner.translate((0, 0, TOTAL_HEIGHT / 2.0))
    
    # 3. 中空シリンダー
    cyl = outer.cut(inner)
    return cyl

# プレートの作成（Z=0からZ=BASE_THICKNESSまで）
plate = cq.Workplane("XY").box(PLATE_WIDTH, PLATE_DEPTH, BASE_THICKNESS, centered=(True, True, False))

# 各外径の中空シリンダーを生成
cyl_295 = create_hollow_cylinder(29.5)
cyl_296 = create_hollow_cylinder(29.6)

# プレートに配置して結合 (Z=0 から配置して完全に交差させる)
# 配置間隔は 30mm (中心は -15.0, 15.0)
result = (plate
          .union(cyl_295.translate((-15.0, 0, 0)))
          .union(cyl_296.translate((15.0, 0, 0)))
         )

# プレート部分にも内径の貫通穴を開けて完全な「筒抜け」にする
r_inner_295 = (29.5 - 2.0 * SOCKET_WALL) / 2.0
r_inner_296 = (29.6 - 2.0 * SOCKET_WALL) / 2.0

inner_cut_295 = cq.Workplane("XY").cylinder(height=BASE_THICKNESS + 0.2, radius=r_inner_295, centered=(True, True, True)).translate((-15.0, 0, BASE_THICKNESS / 2.0))
inner_cut_296 = cq.Workplane("XY").cylinder(height=BASE_THICKNESS + 0.2, radius=r_inner_296, centered=(True, True, True)).translate((15.0, 0, BASE_THICKNESS / 2.0))

result = result.cut(inner_cut_295).cut(inner_cut_296)

# 識別用のマーク（深さ1mmのデボス穴）を一括で彫る
# 29.5mm (x=-15.0) -> 1個
# 29.6mm (x= 15.0) -> 2個
points = [
    (-15.0, -14),               # 29.5用 (1個)
    (13.5, -14), (16.5, -14)    # 29.6用 (2個)
]

result = (result
          .faces(">Z")
          .workplane()
          .pushPoints(points)
          .rect(1.5, 1.5)
          .cutBlind(-1.0)) # 上面から下方向へ1mmカット

# OCP CAD Viewerでプレビュー
try:
    from ocp_vscode import show_object
    show_object(result)
except ImportError:
    pass

# STEPファイルとして出力
output_dir = os.path.dirname(__file__)
output_path = os.path.join(output_dir, "size_test.step")
cq.exporters.export(result, output_path)
print(f"Exported STEP to {output_path}")
