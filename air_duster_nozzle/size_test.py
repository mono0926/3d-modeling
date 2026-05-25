import cadquery as cq
import os

# パラメータ
BASE_THICKNESS = 2.0   # ベースプレートの厚さ
TOTAL_HEIGHT = 17.0    # テストシリンダー全体の高さ（ベースプレート埋め込み分2mmを含む、露出高15mm）
PLATE_WIDTH = 150.0
PLATE_DEPTH = 45.0

def create_cylinder(diameter):
    radius = diameter / 2.0
    # Z=0 から TOTAL_HEIGHT までの円柱にするため、centered=True で作ってからZ方向に移動
    cyl = cq.Workplane("XY").cylinder(height=TOTAL_HEIGHT, radius=radius, centered=(True, True, True))
    cyl = cyl.translate((0, 0, TOTAL_HEIGHT / 2.0))
    
    # 差し込みやすくするために上端を1.0mm面取り
    cyl = cyl.edges(">Z").chamfer(1.0)
    return cyl

# プレートの作成（Z=0からZ=BASE_THICKNESSまで）
plate = cq.Workplane("XY").box(PLATE_WIDTH, PLATE_DEPTH, BASE_THICKNESS, centered=(True, True, False))

# 各外径のシリンダーを生成
cyl_291 = create_cylinder(29.1)
cyl_292 = create_cylinder(29.2)
cyl_293 = create_cylinder(29.3)
cyl_294 = create_cylinder(29.4)

# プレートに配置して結合 (Z=0 から配置して完全に交差させる)
# 配置間隔は 35mm (中心は -52.5, -17.5, 17.5, 52.5)
result = (plate
          .union(cyl_291.translate((-52.5, 0, 0)))
          .union(cyl_292.translate((-17.5, 0, 0)))
          .union(cyl_293.translate((17.5, 0, 0)))
          .union(cyl_294.translate((52.5, 0, 0)))
         )

# 識別用のマーク（深さ1mmのデボス穴）を一括で彫る
# 29.1mm (x=-52.5) -> 1個
# 29.2mm (x=-17.5) -> 2個
# 29.3mm (x= 17.5) -> 3個
# 29.4mm (x= 52.5) -> 4個
points = [
    (-52.5, -14),                       # 29.1用 (1個)
    (-19.5, -14), (-15.5, -14),         # 29.2用 (2個)
    (14.5, -14), (17.5, -14), (20.5, -14), # 29.3用 (3個)
    (48.0, -14), (51.0, -14), (54.0, -14), (57.0, -14) # 29.4用 (4個)
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
