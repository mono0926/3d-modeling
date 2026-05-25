import cadquery as cq
import os

# ==================== パラメータ定義 ====================
PTFE_INSERT_DEPTH = 15.0  # チューブを差し込む深さ
BLOCK_HEIGHT = PTFE_INSERT_DEPTH + 2.0  # ブロック全体の高さ (17.0mm)
BLOCK_WIDTH = 80.0
BLOCK_DEPTH = 20.0
AIR_HOLE = 2.5            # 貫通空気穴の直径

# 4つのバリエーション (入口直径, 奥直径)
# 3Dプリントの太り・収縮を考慮し、設計値 (4.15mm, 3.85mm) を中心に0.1mm刻みでシフト
variations = [
    (4.05, 3.75),  # 穴1: タイト (全体に -0.1mm)
    (4.15, 3.85),  # 穴2: 標準 (本番設計値)
    (4.25, 3.95),  # 穴3: 少しルーズ (全体に +0.1mm)
    (4.35, 4.05)   # 穴4: ルーズ (全体に +0.2mm)
]

# ==================== モデリング ====================
# 1. ベースブロックの作成 (Z=0 から BLOCK_HEIGHT まで)
block = cq.Workplane("XY").box(BLOCK_WIDTH, BLOCK_DEPTH, BLOCK_HEIGHT, centered=(True, True, False))

# 2. 各バリエーションの穴を配置して切り抜く
# 配置間隔は 18.0mm (中心位置: -27.0, -9.0, 9.0, 27.0)
x_positions = [-27.0, -9.0, 9.0, 27.0]

for x, (in_dia, out_dia) in zip(x_positions, variations):
    # PTFEチューブ差し込み用のテーパー穴（Z=2 から Z=17 まで）
    # 底（Z=2）の半径は out_dia/2.0、上端（Z=17）の半径は in_dia/2.0
    ptfe_hole = (cq.Workplane("XY")
                 .workplane(offset=2.0)
                 .circle(out_dia / 2.0)
                 .workplane(offset=PTFE_INSERT_DEPTH)
                 .circle(in_dia / 2.0)
                 .loft(ruled=True)
                )
    
    # 底部の貫通空気穴（Z=0 から Z=2 まで）
    air_hole = (cq.Workplane("XY")
                .cylinder(height=2.0, radius=AIR_HOLE / 2.0, centered=(True, True, True))
                .translate((0, 0, 1.0)) # Z=0〜2に配置
               )
    
    # 穴をブロックから差し引く
    block = block.cut(ptfe_hole.translate((x, 0, 0)))
    block = block.cut(air_hole.translate((x, 0, 0)))

# 3. 識別用のマーク（深さ1mmのデボス穴）を一括で彫る
# 各穴の手前 (y = -7.0) に、凹みを 1, 2, 3, 4 個配置
points = [
    (-27.0, -7.0),                              # 穴1用 (1個)
    (-10.5, -7.0), (-7.5, -7.0),                # 穴2用 (2個)
    (7.5, -7.0), (9.0, -7.0), (10.5, -7.0),     # 穴3用 (3個)
    (24.0, -7.0), (26.0, -7.0), (28.0, -7.0), (30.0, -7.0) # 穴4用 (4個)
]

block = (block
         .faces(">Z")
         .workplane()
         .pushPoints(points)
         .rect(1.5, 1.5)
         .cutBlind(-1.0)
        )

# OCP CAD Viewerでプレビュー
try:
    from ocp_vscode import show_object
    show_object(block)
except ImportError:
    pass

# STEPファイルとして出力
output_dir = os.path.dirname(__file__)
output_path = os.path.join(output_dir, "ptfe_test.step")
cq.exporters.export(block, output_path)
print(f"Exported STEP to {output_path}")
