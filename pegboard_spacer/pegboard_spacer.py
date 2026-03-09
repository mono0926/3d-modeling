"""
設計要件:
    - ドリームウェア製有孔ボード（WJ-SB7WH）を本棚に固定するためのスペーサー。
    - 有孔ボードの穴（5mm径、25mm間隔）に嵌まるピンを設け、ずり落ちを防止。
    - 厚さ6mmのベースに、両面2mmの魔法のテープを貼ることで、背面スペース10mmを確保。
    - 最新の3Dプリンター（Bambu Lab P2S 等）での出力を想定。

推奨フィラメント:
    - PLA または PETG (強度と印刷のしやすさのバランスから推奨)。

推奨スライサー設定:
    - 壁ループ (Wall Loops): 3 (強度の確保)
    - インフィル (Infill): 25% (グリッドまたはジャイロイド)
    - サポート (Support): 不要 (ピンの高さが低いため、ブリッジ/オーバーハング設定で対応可能)

印刷統計（予想）:
    - pegboard_spacer.step: 印刷時間 約15分、フィラメント使用量 約5g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import cadquery as cq
import os
from ocp_vscode import show_object

# パラメーター定義
WIDTH = 60.0
HEIGHT = 30.0
BASE_THICKNESS = 6.0

PIN_DIAMETER = 4.8  # 5mm穴に対して適度なクリアランス
PIN_HEIGHT = 3.0    # 2mmテープを突き抜け、1mm厚のボードに収まる高さ
PIN_PITCH = 25.0    # 有孔ボードの規格

# モデル作成
result = (
    cq.Workplane("XY")
    .box(WIDTH, HEIGHT, BASE_THICKNESS)
    .faces(">Z")
    .workplane()
    .pushPoints([(-PIN_PITCH / 2, 0), (PIN_PITCH / 2, 0)])
    .circle(PIN_DIAMETER / 2)
    .extrude(PIN_HEIGHT)
    .edges("|Z or >Z")
    .fillet(0.5)  # ピンの根元とエッジにわずかなフィレット
)

# プレビュー表示
show_object(result, name="pegboard_spacer")

# STEPファイル出力
output_dir = os.path.dirname(__file__)
output_path = os.path.join(output_dir, "pegboard_spacer.step")
cq.exporters.export(result, output_path)

print(f"Exported to {output_path}")
