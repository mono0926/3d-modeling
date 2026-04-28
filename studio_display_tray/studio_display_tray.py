import cadquery as cq
from ocp_vscode import show_object
import math
import os

"""
設計要件:
    - Apple Studio Display「傾きと高さを調整できるスタンド」専用設計。
    - V4.2.1: 支柱逃げを R5.0 (半径) に修正。棚板を2mm厚とし、前端に6mmの「段差（リップ）」を追加。
    - 確定寸法 (V4.2.1): 横152mm, 高さ105mm, 奥175.71mm, R5.0/R10
"""

# ---- 確定パラメータ (V4.2.1) ----
WIDTH = 152.0
DEPTH = 175.71
HEIGHT = 105.0
THICKNESS = 2.0        # 壁厚 2mm
FRONT_ANGLE = 60.0     # 前面傾斜 60度
SHELF_HEIGHT = 45.0    # 棚の取付高さ
LIP_HEIGHT = 6.0       # 前端の「段差」高さ
PILLAR_R = 5.0         # 垂直部分の内径 (半径) 5.0mm (確定)
BASE_CORNER_R = 10.0   # 底面の角丸の内径 (半径) 10mm

# 前面の斜めカット計算
slant_offset = HEIGHT / math.tan(math.radians(FRONT_ANGLE))
depth_top = DEPTH - slant_offset

# 1. 外形ソリッドの生成
outer_profile = (cq.Workplane("YZ")
                .lineTo(0, HEIGHT)
                .lineTo(depth_top, HEIGHT)
                .lineTo(DEPTH, 0)
                .close())
body = outer_profile.extrude(WIDTH / 2.0, both=True)

# エッジ選択用の座標
x_edge = WIDTH / 2.0
y_front = DEPTH
z_mid = HEIGHT / 2.0

# 背面垂直エッジのフィレット（意匠R3）
body = body.edges("|Z and <Y").fillet(3.0)

# 前面斜めエッジのフィレット（R10）
front_selector = (cq.NearestToPointSelector((-x_edge, y_front, z_mid)) +
                  cq.NearestToPointSelector((x_edge, y_front, z_mid)))
body = body.edges(front_selector).fillet(BASE_CORNER_R)

# 支柱の付け根R5を逃がすための背面底部フィレット
# 指定の R5.0 を適用（マージンなし）
body = body.edges("<Y and <Z").fillet(PILLAR_R)

# 2. 内側のくり抜き
inner_h = HEIGHT - 2 * THICKNESS
inner_y_start = THICKNESS
inner_y_end = DEPTH + 20.0

inner_profile = (cq.Workplane("YZ")
                .moveTo(inner_y_start, THICKNESS)
                .lineTo(inner_y_start, HEIGHT - THICKNESS)
                .lineTo(depth_top, HEIGHT - THICKNESS)
                .lineTo(inner_y_end, HEIGHT - THICKNESS)
                .lineTo(inner_y_end, THICKNESS)
                .close())

inner_solid = inner_profile.extrude((WIDTH - 2 * THICKNESS) / 2.0, both=True)
body = body.cut(inner_solid)

# 3. 棚板（2mm厚 ＋ 前端に6mmの段差リップ）
shelf_w = WIDTH - 2 * THICKNESS
shelf_d = DEPTH * 0.8

# ベースの2mm厚板
shelf_base = (cq.Workplane("XY")
              .rect(shelf_w, shelf_d)
              .extrude(THICKNESS))

# 前端に6mmのリップ（厚さ2mm）を追加
lip = (cq.Workplane("XY")
       .rect(shelf_w, THICKNESS)
       .extrude(LIP_HEIGHT)
       .translate((0, shelf_d/2 - THICKNESS/2, THICKNESS)))

shelf = shelf_base.union(lip)

# 15度傾斜させて配置
shelf = (shelf
         .translate((0, DEPTH/2, SHELF_HEIGHT))
         .rotate((0, 0, SHELF_HEIGHT), (1, 0, SHELF_HEIGHT), 15.0))

# 本体内部でトリミングして合体
shelf_fitted = shelf.intersect(inner_solid)
body = body.union(shelf_fitted)

# ---- 仕上げ ----
# (形状干渉を避けるため微細フィレットは省略)

# 出力
show_object(body, name="Studio Display Tray V4.2.1 FINAL")
output_path = os.path.join(os.path.dirname(__file__), "studio_display_tray.step")
cq.exporters.export(body, output_path)

print(f"究極のモデル(V4.2.1)の生成が完了しました！\n出力先: {output_path}")
