"""
設計要件:
    - 山崎実業 Tower シリーズ「フィルムフック 鍋蓋ホルダー」と同等の機能を持つモデル。
    - 磁石テープで壁に取り付けるため、背面は完全にフラットな板状とする。
    - 14cm〜30cmの鍋蓋を1枚収納可能。
    - サポート材不要で印刷できるよう、背面を底面（Z=0）として設計。

推奨フィラメント:
    - PLA, PETG
    - 耐熱性や強度を考慮すると PETG 推奨。

推奨スライサー設定:
    - 背面を下にしてビルドプレートへ配置。
    - ウォールループ (Wall loops): 4
    - インフィル (Infill): 15% (Gyroid)
    - サポート (Support): なし

印刷統計（予想）:
    - tower_pot_lid_holder.step: 印刷時間 約2時間、フィラメント使用量 約70g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os
from ocp_vscode import show_object

# ==========================================
# Parameter Definitions (パラメーター設定)
# ==========================================

# 全体寸法 (Tower製品を参考)
WIDTH = 135.0
HEIGHT = 140.0
DEPTH = 62.0

# 厚み設定
BASE_THICKNESS = 4.0      # 背面板の厚み（しっかり磁石を貼れるように）
FRAME_THICKNESS = 8.0     # フレームの幅
ARM_THICKNESS = 8.0       # 前に突き出すアーム部の幅

# ==========================================
# Geometry Generation (形状生成)
# ==========================================

# 1. 背面板 (Base Plate)
# 磁石テープをしっかり貼れるようにフラットな長方形
base_plate = cq.Workplane("XY").box(WIDTH, HEIGHT, BASE_THICKNESS, centered=(True, True, False))

# 2. 本体アーム部 (U字フレーム型)
# 背面（Z=BASE_THICKNESS）から上に構築
# Towerの鍋フタホルダーは、左右の柱と下部の受け、そして「蓋の手前への転落防止のツメ」を持つ

arm_depth = DEPTH - BASE_THICKNESS

# 左右の壁（柱）
# 外側はまっすぐ、内側は蓋が入るように大きくU字に切り欠く
u_shape = (
    cq.Workplane("XY", origin=(0, 0, BASE_THICKNESS))
    .box(WIDTH, HEIGHT, arm_depth, centered=(True, True, False))
)

# 内側を切り抜く（U字カット）
# 上からスロープ状に下がり、底で支える
cutout_width = WIDTH - FRAME_THICKNESS * 2
cutout_height = HEIGHT - FRAME_THICKNESS * 2

# 切り抜き形状
cutout = (
    cq.Workplane("XY", origin=(0, FRAME_THICKNESS, BASE_THICKNESS))
    .moveTo(-cutout_width/2, HEIGHT/2)
    # 斜めに下る
    .lineTo(-cutout_width/4, -HEIGHT/2 + FRAME_THICKNESS)
    .lineTo(cutout_width/4, -HEIGHT/2 + FRAME_THICKNESS)
    .lineTo(cutout_width/2, HEIGHT/2)
    .close()
    .extrude(arm_depth + 10) # 貫通させる
)

# まず大きな直方体から斜めカットを引く
holder = base_plate.union(u_shape.cut(cutout))

# 3. 傾斜をつける（蓋が壁側に寄りかかるように）
# 現在は平らなアームなので、手前（Z方向の高い位置）に向かって斜面を作る
# 不要な部分を斜めに切り落とすことで、アーム上面を壁に向かって下るスロープにする
slope_cut = (
    cq.Workplane("YZ", origin=(0, 0, BASE_THICKNESS))
    .moveTo(-HEIGHT/2, arm_depth*1.5)
    .lineTo(HEIGHT/2, arm_depth) # 手前側が高い
    .lineTo(HEIGHT/2, 0)
    .lineTo(-HEIGHT/2, 0)
    .close()
    .extrude(WIDTH + 10, both=True)
)
# このslope_cutの形状と共通部分をとることで、斜めカットを適用
holder = holder.intersect(slope_cut)


# 4. 前への転落防止リップ（ツメ）
# 蓋が手前に落ちないように、スロープの手前端に高さを持たせる
lip_height = 15.0
lip_width = FRAME_THICKNESS

# 左右のリップ
lip_L = (
    cq.Workplane("XY", origin=(-WIDTH/2 + lip_width/2, -HEIGHT/2 + FRAME_THICKNESS/2, BASE_THICKNESS))
    .box(lip_width, FRAME_THICKNESS, arm_depth + lip_height, centered=(True, True, False))
)
lip_R = (
    cq.Workplane("XY", origin=(WIDTH/2 - lip_width/2, -HEIGHT/2 + FRAME_THICKNESS/2, BASE_THICKNESS))
    .box(lip_width, FRAME_THICKNESS, arm_depth + lip_height, centered=(True, True, False))
)

holder = holder.union(lip_L).union(lip_R)

# 5. 中央のW字/V字の支え
# 小さい蓋（14cmなど）が落ちないように、中央にV字形の支えを追加
v_support = (
    cq.Workplane("XY", origin=(0, -HEIGHT/2 + FRAME_THICKNESS, BASE_THICKNESS))
    .moveTo(-WIDTH/4, HEIGHT/3)
    .lineTo(0, -FRAME_THICKNESS)
    .lineTo(WIDTH/4, HEIGHT/3)
    .lineTo(WIDTH/4 + FRAME_THICKNESS, HEIGHT/3)
    .lineTo(0, -FRAME_THICKNESS - FRAME_THICKNESS)
    .lineTo(-WIDTH/4 - FRAME_THICKNESS, HEIGHT/3)
    .close()
    .extrude(FRAME_THICKNESS * 1.5) # 手前まで出さない
)
holder = holder.union(v_support)

# 6. 面取り（丸める）
# 鋭角を落として安全にする
try:
    holder = holder.edges("|Z").fillet(2.0)
except Exception:
    pass

try:
    # 蓋が当たる部分をなだらかにする
    holder = holder.edges(">Z").fillet(1.5)
except Exception:
    pass

# ==========================================
# Export (ファイル出力)
# ==========================================

show_object(holder)

output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tower_pot_lid_holder.step")
print(f"Exporting to: {output_file}")
cq.exporters.export(holder, output_file)
print("Done!")
