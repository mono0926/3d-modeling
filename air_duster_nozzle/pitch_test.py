import cadquery as cq
import os

# パラメータ
OUTER_DIAMETER = 29.3  # ユーザー測定の付属ノズル外径
RADIUS_OUTER = OUTER_DIAMETER / 2.0
BASE_THICKNESS = 2.0   # ベースプレートの厚さ
# ねじをZ=0から作成し、ベースプレートと完全に交差させる
TOTAL_HEIGHT = 14.0    # ねじ全体の高さ（ベースプレート埋め込み分2mmを含む）
THREAD_HEIGHT = 10.0   # ねじ山を切る高さ（Z=0からZ=10.0まで）
PLATE_WIDTH = 120.0
PLATE_DEPTH = 40.0

def create_screw(pitch):
    # ねじ山の高さ (0.6 * pitch)
    thread_depth = 0.6 * pitch
    r_base = RADIUS_OUTER - thread_depth
    w_base = 0.8 * pitch  # 底辺幅（隣接するねじ山との間に少し隙間を空ける）

    # 1. ベース円柱とガイド用テーパーの作成
    # 高さを TOTAL_HEIGHT にし、上面エッジを大きく面取りして導入ガイドにする
    cyl = cq.Workplane("XY").cylinder(height=TOTAL_HEIGHT, radius=r_base, centered=(True, True, False))
    cyl = cyl.edges(">Z").chamfer(1.5)

    # 2. らせんねじ山の作成
    # Z=0 から Z=THREAD_HEIGHT までらせんを作成
    path = cq.Wire.makeHelix(pitch=pitch, height=THREAD_HEIGHT, radius=r_base)

    # XZ平面に三角形の断面を配置
    profile = (cq.Workplane("XZ")
               .moveTo(r_base, -w_base / 2)
               .lineTo(RADIUS_OUTER, 0)
               .lineTo(r_base, w_base / 2)
               .close())

    # らせんパスに沿ってスイープ
    thread = profile.sweep(path, isFrenet=True)

    # ベース円柱とねじ山を結合
    screw = cyl.union(thread)

    return screw

# プレートの作成（Z=0からZ=BASE_THICKNESSまで）
plate = cq.Workplane("XY").box(PLATE_WIDTH, PLATE_DEPTH, BASE_THICKNESS, centered=(True, True, False))

# 各ピッチのねじを生成して配置 (Z=0 から配置してプレートと交差させる)
screw_15 = create_screw(1.5).translate((-35, 0, 0))
screw_20 = create_screw(2.0).translate((0, 0, 0))
screw_30 = create_screw(3.0).translate((35, 0, 0))

# プレートに結合 (重なりがあるため安全に結合可能)
result = plate.union(screw_15).union(screw_20).union(screw_30)

# 識別用のマーク（深さ1mmのデボス穴）を一括で彫る
# P1.5: x=-35 に1個
# P2.0: x=0 の周辺に2個
# P3.0: x=35 の周辺に3個
points = [
    (-35, -12),                # P1.5用
    (-2.0, -12), (2.0, -12),   # P2.0用
    (32.0, -12), (35.0, -12), (38.0, -12) # P3.0用
]

result = (result
          .faces(">Z")
          .workplane()
          .pushPoints(points)
          .rect(2, 2)
          .cutBlind(-1.0)) # 上面から下方向へ1mmカット

# OCP CAD Viewerでプレビュー
try:
    from ocp_vscode import show_object
    show_object(result)
except ImportError:
    pass

# STEPファイルとして出力
output_dir = os.path.dirname(__file__)
output_path = os.path.join(output_dir, "pitch_test.step")
cq.exporters.export(result, output_path)
print(f"Exported STEP to {output_path}")
