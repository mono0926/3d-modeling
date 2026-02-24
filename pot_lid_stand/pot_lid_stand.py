"""
設計要件:
    - 鍋蓋（直径20-30cm、厚さ4cmまで）を支えるための壁掛け用スタンド。
    - 鉄の壁に対して背面に磁石テープを貼付け可能。
    - **力学と安定性**:
      アームの溝を手前（リップ側）に向かって深く下るスロープとし、
      蓋が自重で壁と反対側に滑ることで、自然と蓋の上部が「壁に真っ直ぐ寄りかかる」姿勢を担保する。
    - **曲線的フィット感 (赤丸部の改善)**:
      内部の切り欠きを単純な直角ではなく、巨大なU字（サドル型）の曲面でシームレスに繋ぐ。
      底面から手前のリップに至るまで、一切の鋭角（角）をなくし、どのような曲面の蓋でも完璧に定着させる。
    - サポート材不要で印刷できるように壁付け面を下（Z=0）にして設計。

推奨フィラメント:
    - PLA, PETG (実用強度として十分。台所なので耐熱性が必要ならPETG推奨)

推奨スライサー設定:
    - 壁面（背面）を下にしてビルドプレートへ配置。
    - ウォールループ（Wall loops）: 4 (アーム部の強度確保のため)
    - インフィル（Infill）: 15%〜20% Gyroid
    - サポート（Support）: なし

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os
from ocp_vscode import show_object

# ==========================================
# Parameter Definitions (パラメーター設定)
# ==========================================

STAND_WIDTH = 140.0    # スタンドの全幅（ややコンパクトに）
STAND_HEIGHT = 50.0    # ベースプレートの縦幅（深すぎない高さへ変更）
TOTAL_DEPTH = 45.0     # 壁からリップ先端までの奥行き（4cmの蓋にジャスト）

# 外側の壁厚（アームの左右の厚み）を薄くし、大きな径の蓋でも干渉しにくくする
# 谷（内寸）の幅を広げる。壁厚 ＝ (STAND_WIDTH - VALLEY_WIDTH) / 2
VALLEY_WIDTH = 124.0   # 中央のU字の幅（全幅140mmに対し左右8mmの薄壁）

# ==========================================
# Geometry Generation (ロフトによる美しい曲面生成)
# ==========================================

# 断面形状（U字のくり抜きがある長方形）を生成する関数
def make_profile_wire(z, y_under, y_valley):
    v2 = VALLEY_WIDTH / 2.0
    s2 = STAND_WIDTH / 2.0
    return (
        cq.Workplane("XY", origin=(0, 0, z))
        .moveTo(-s2, y_under)           # 左下
        .lineTo(s2, y_under)            # 右下
        .lineTo(s2, STAND_HEIGHT)       # 右上
        .lineTo(v2, STAND_HEIGHT)       # 右アームの内側端
        # U字の谷を3点アーク（円弧）で描画し、完全になだらかな曲線にする
        .threePointArc((0, y_valley), (-v2, STAND_HEIGHT))
        .lineTo(-s2, STAND_HEIGHT)      # 左上
        .close()
    )

# 4点のZ座標（奥行き）に少しずつ変化するプロファイルを設定し、
# それらを曲面（スプライン）でシームレスに繋ぐ（Loft）ことでネイティブな曲面を作る。

# 1. 背面（壁に接する面）: マグネットを貼れるようフラットだが、上でU字に開いている。
w_wall = make_profile_wire(z=0.0, y_under=0.0, y_valley=35.0)

# 2. 溝の最下点（谷底）: ここを一番低くすることで蓋が手前に滑る。浅めに設定。
w_bottom = make_profile_wire(z=25.0, y_under=7.0, y_valley=15.0)

# 3. リップの内壁ピーク: 谷底からなだらかに立ち上がる。
w_lip_inner = make_profile_wire(z=37.0, y_under=9.0, y_valley=42.0)

# 4. リップの前面（一番手前）: 平らな正面を作る。
w_lip_outer = make_profile_wire(z=45.0, y_under=10.0, y_valley=42.0)

# プロファイルを束ねてロフト化（ruled=False によりプロファイル間が有機的な三次曲面で保管されます）
wires = [
    w_wall.wires().val(),
    w_bottom.wires().val(),
    w_lip_inner.wires().val(),
    w_lip_outer.wires().val()
]
body = cq.Solid.makeLoft(wires, ruled=False)

# CadQueryワークプレーンオブジェクトに変換
holder = cq.Workplane("XY").add(body)

# ==========================================
# Export (ファイル出力)
# ==========================================

try:
    show_object(holder, name="Pot Lid Stand Curved Organic")
except Exception:
    pass

output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pot_lid_stand.step")
print(f"Exporting to: {output_file}")
cq.exporters.export(holder, output_file)
print("Done!")
