import cadquery as cq
import os

"""
設計要件:
    - 13mm径、長さ151mmのアクリルマーカーを6本収納。
    - パレット（色見本用窪み）と色番号用ラベルエリアを両端に配置。
    - 中央にPETG向けの適度なしなりを持たせたスナップフィット（Cクリップ）を配置。
    - 2つのケースを重ねて12本用携帯ケースになる（同一モデルを2つ印刷して向かい合わせる設計）。
    - 四隅に5x2mmのネオジム磁石用ポケットを配置し、ズレ防止の合わせピン・穴も搭載。

推奨フィラメント:
    - PETG (スナップフィットのしなりと耐久性に最適)
    - PLAでも印刷可能ですが、スナップ部がやや硬くなる可能性があります。

推奨スライサー設定:
    - 壁（Wall loops）: 3〜4
    - インフィル: 15%〜20% (Gyroid推奨)
    - サポート: 不要（印刷面を下にして配置）

磁石の接着について（重要）:
    - 重ねた時に反発しないよう、片側（例えば左側2箇所）はN極を上に、反対側（右側2箇所）はS極を上にして接着してください。
    - こうすることで、同じケースをひっくり返して重ねた際に必ずNとSが合わさります。

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# --- Parameters ---
PEN_D = 13.0
PEN_L = 151.0
N_PENS = 6
PITCH = 18.0

PEN_CLEARANCE = 0.6
GROOVE_D = PEN_D + PEN_CLEARANCE

CLIP_D = 13.1  # 保持力のためのタイトな径
CLIP_OPENING = 12.0
SNAP_L = 12.0
CLIP_BLOCK_W = 16.0  # クリップ同士の隙間を確保し、しなりを許容する

BASE_T = 2.5
GROOVE_H = 3.5
WALL_Z = 16.5
WALL_T = 6.0

PALETTE_L = 16.0
CLEARANCE_L = 2.0
TOTAL_PEN_L = PEN_L + CLEARANCE_L
INNER_L = TOTAL_PEN_L + 2 * PALETTE_L
INNER_W = N_PENS * PITCH

TOTAL_L = INNER_L + 2 * WALL_T
TOTAL_W = INNER_W + 2 * WALL_T

GROOVE_TOP_Z = BASE_T + GROOVE_H
PEN_Z = BASE_T + GROOVE_D / 2.0
CLIP_BLOCK_H = PEN_Z + 4.0 - GROOVE_TOP_Z

# --- Modeling ---

# 1. 外形ベース
sk = cq.Sketch().rect(TOTAL_W, TOTAL_L).vertices().fillet(4.0)
body = cq.Workplane("XY").placeSketch(sk).extrude(WALL_Z)

# 2. 内側のくり抜き（壁の形成）
inner_sk = cq.Sketch().rect(INNER_W, INNER_L).vertices().fillet(2.0)
pocket = cq.Workplane("XY", origin=(0, 0, GROOVE_TOP_Z)).placeSketch(inner_sk).extrude(WALL_Z - GROOVE_TOP_Z)
body = body.cut(pocket)

# 3. ペン溝とクリップの形成
xs = [(i - (N_PENS - 1) / 2.0) * PITCH for i in range(N_PENS)]

for x in xs:
    # クリップ用ブロックの追加
    clip_block = cq.Workplane("XY", origin=(x, 0, GROOVE_TOP_Z + CLIP_BLOCK_H/2)).box(CLIP_BLOCK_W, SNAP_L, CLIP_BLOCK_H)
    body = body.union(clip_block)
    
    # 中央クリップ部の円柱カット
    clip_cyl = cq.Workplane("XZ", origin=(x, 0, PEN_Z)).circle(CLIP_D / 2.0).extrude(TOTAL_PEN_L/2.0, both=True)
    body = body.cut(clip_cyl)
    
    # クリップ上部の開口部カット
    clip_slot = cq.Workplane("XY", origin=(x, 0, PEN_Z)).rect(CLIP_OPENING, SNAP_L).extrude(WALL_Z)
    body = body.cut(clip_slot)
    
    # クリップ挿入部の面取り（リードイン）
    lead_in = (
        cq.Workplane("XZ", origin=(x, 0, GROOVE_TOP_Z + CLIP_BLOCK_H - 1.5))
        .moveTo(-CLIP_OPENING/2.0, 0)
        .lineTo(-14.0/2.0, 1.5)
        .lineTo(14.0/2.0, 1.5)
        .lineTo(CLIP_OPENING/2.0, 0)
        .close()
        .extrude(SNAP_L/2.0, both=True)
    )
    body = body.cut(lead_in)
    
    # クリップ部以外の緩い溝のカット
    y_start = SNAP_L / 2.0
    y_end = TOTAL_PEN_L / 2.0
    y_len = y_end - y_start
    y_center = y_start + y_len / 2.0
    
    # Yプラス側
    loose_cyl_1 = cq.Workplane("XZ", origin=(x, y_center, PEN_Z)).circle(GROOVE_D / 2.0).extrude(y_len / 2.0, both=True)
    loose_slot_1 = cq.Workplane("XY", origin=(x, y_center, PEN_Z)).rect(GROOVE_D, y_len).extrude(WALL_Z)
    body = body.cut(loose_cyl_1).cut(loose_slot_1)
    
    # Yマイナス側
    loose_cyl_2 = cq.Workplane("XZ", origin=(x, -y_center, PEN_Z)).circle(GROOVE_D / 2.0).extrude(y_len / 2.0, both=True)
    loose_slot_2 = cq.Workplane("XY", origin=(x, -y_center, PEN_Z)).rect(GROOVE_D, y_len).extrude(WALL_Z)
    body = body.cut(loose_cyl_2).cut(loose_slot_2)
    
    # パレットと色番号ラベル用の窪み
    for sign in [1, -1]:
        # 丸いパレット窪み
        cy = sign * (TOTAL_PEN_L / 2.0 + 6.0)
        palette = cq.Workplane("XY", origin=(x, cy, GROOVE_TOP_Z)).circle(4.5).extrude(-1.0)
        body = body.cut(palette)
        
        # 四角いラベル窪み
        ry = sign * (TOTAL_PEN_L / 2.0 + 13.0)
        label = cq.Workplane("XY", origin=(x, ry, GROOVE_TOP_Z)).rect(12.0, 4.0).extrude(-0.5)
        body = body.cut(label)

# 4. マグネット穴と位置合わせピン
MAGNET_D = 5.2
MAGNET_H = 2.2

hole_centers = [
    ( INNER_W/2 + WALL_T/2,  INNER_L/2 + WALL_T/2),
    (-INNER_W/2 - WALL_T/2,  INNER_L/2 + WALL_T/2),
    ( INNER_W/2 + WALL_T/2, -INNER_L/2 - WALL_T/2),
    (-INNER_W/2 - WALL_T/2, -INNER_L/2 - WALL_T/2),
]

for hx, hy in hole_centers:
    magnet_hole = cq.Workplane("XY", origin=(hx, hy, WALL_Z)).circle(MAGNET_D/2.0).extrude(-MAGNET_H)
    body = body.cut(magnet_hole)

# 位置合わせピン (2つのケースを合わせた時にピンと穴が噛み合う設計)
pin_y_offsets = [INNER_L / 4.0, -INNER_L / 4.0]
for py in pin_y_offsets:
    # 左側の壁にピンを配置
    pin = cq.Workplane("XY", origin=(-(INNER_W/2 + WALL_T/2), py, WALL_Z)).circle(1.5).extrude(2.0)
    pin = pin.edges(">Z").chamfer(0.5)
    body = body.union(pin)
    
    # 右側の壁に穴を配置
    hole = cq.Workplane("XY", origin=(INNER_W/2 + WALL_T/2, py, WALL_Z)).circle(1.7).extrude(-2.5)
    body = body.cut(hole)

# 5. 外周底面のフィレット (手触り向上)
body = body.edges("<Z").fillet(1.5)

# --- Output ---
try:
    from ocp_vscode import show_object
    show_object(body, name="Acrylic Marker Case")
except ImportError:
    pass

out_dir = os.path.dirname(__file__)
step_path = os.path.join(out_dir, "acrylic_marker_case.step")
cq.exporters.export(body, step_path)
print(f"Exported to {step_path}")
