import cadquery as cq
import os

# ==================== パラメータ定義 ====================
PTFE_INSERT_DEPTH = 15.0  # チューブを差し込む深さ
TOTAL_HEIGHT = PTFE_INSERT_DEPTH + 2.0  # ソケット全体の高さ (17.0mm)
PTFE_OD = 8.0             # 外径 (肉厚約2mmを確保)
AIR_HOLE = 2.5            # 貫通空気穴の直径
CONN_THICKNESS = 1.2      # 連結用プレートの厚さ
CONN_WIDTH = 6.0          # 連結用プレートの幅
SPACING = 15.0            # 各円筒の間隔

# 4つのバリエーション (入口直径, 奥直径)
variations = [
    (4.05, 3.75),  # 穴1: タイト
    (4.15, 3.85),  # 穴2: 標準 (本番設計値)
    (4.25, 3.95),  # 穴3: 少しルーズ
    (4.35, 4.05)   # 穴4: ルーズ
]

def create_ptfe_socket(in_dia, out_dia):
    # 1. 外側の円筒 (Z=0 から TOTAL_HEIGHT)
    # Z位置ズレによるブーリアンエラーを防ぐため、centered=True で作ってからZ方向に移動
    outer = cq.Workplane("XY").cylinder(height=TOTAL_HEIGHT, radius=PTFE_OD/2.0, centered=(True, True, True))
    outer = outer.translate((0, 0, TOTAL_HEIGHT / 2.0))
    
    # 2. PTFEチューブ差し込み用のテーパー穴（Z=2 から Z=17）
    # 重なりを設けるため、z=2 から開始
    ptfe_hole = (cq.Workplane("XY")
                 .workplane(offset=2.0)
                 .circle(out_dia / 2.0)
                 .workplane(offset=PTFE_INSERT_DEPTH)
                 .circle(in_dia / 2.0)
                 .loft(ruled=True)
                )
    
    # 3. 貫通空気穴（Z=0 から Z=2）
    # コプラナー面を防ぐため、高さを 2.1mm (少し長め) にして確実に貫通させる
    air_hole = (cq.Workplane("XY")
                .cylinder(height=2.2, radius=AIR_HOLE / 2.0, centered=(True, True, True))
                .translate((0, 0, 1.1))
               )
    
    # 円筒から穴を引く
    socket = outer.cut(ptfe_hole).cut(air_hole)
    return socket

# 4. 連結用リボンプレート (Z=0 から Z=CONN_THICKNESS)
plate_width = SPACING * 3 + PTFE_OD + 4.0  # 約 57.0mm
plate = cq.Workplane("XY").box(plate_width, CONN_WIDTH, CONN_THICKNESS, centered=(True, True, False))

# 5. 各ソケットを生成して配置
x_positions = [-SPACING * 1.5, -SPACING * 0.5, SPACING * 0.5, SPACING * 1.5]
sockets = []
for x, (in_dia, out_dia) in zip(x_positions, variations):
    sockets.append(create_ptfe_socket(in_dia, out_dia).translate((x, 0, 0)))

# 6. プレートとソケットを結合
result = plate
for s in sockets:
    # プレート（厚さ1.2mm）とソケット（Z=0〜17mm）はZ=0〜1.2mmの部分で深く交差するため、安全に結合可能
    result = result.union(s)

# 7. 識別用の穴（繋ぎプレートに開ける小さな1mmの貫通穴）
# 各ソケットの手前（y = -1.8）の位置に 1〜4 個の貫通穴を配置して区別
points = [
    (-SPACING * 1.5, -1.8),                                       # 1個
    (-SPACING * 0.5 - 1.2, -1.8), (-SPACING * 0.5 + 1.2, -1.8),   # 2個
    (SPACING * 0.5 - 2.0, -1.8), (SPACING * 0.5, -1.8), (SPACING * 0.5 + 2.0, -1.8), # 3個
    (SPACING * 1.5 - 3.0, -1.8), (SPACING * 1.5 - 1.0, -1.8), (SPACING * 1.5 + 1.0, -1.8), (SPACING * 1.5 + 3.0, -1.8) # 4個
]

result = (result
          .faces(">Z")
          .workplane()
          .pushPoints(points)
          .rect(1.0, 1.0)
          .cutThruAll()
         )

# OCP CAD Viewerでプレビュー
try:
    from ocp_vscode import show_object
    show_object(result)
except ImportError:
    pass

# STEPファイルとして出力
output_dir = os.path.dirname(__file__)
output_path = os.path.join(output_dir, "ptfe_test.step")
cq.exporters.export(result, output_path)
print(f"Exported STEP to {output_path}")
