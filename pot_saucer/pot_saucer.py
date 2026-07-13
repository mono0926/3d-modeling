from build123d import *
import os
from ocp_vscode import show_object

"""
設計要件:
    - 多肉植物用の鉢に最適な受け皿（デフォルト底面外径100mm）。
    - 室内使用を想定した水漏れ防止機能。
    - 鉢底の通気性を考慮したリブ構造。
    - サポートなしで印刷可能な形状。

推奨フィラメント:
    - PETG (耐水性と耐久性に優れるため推奨)
    - PLA (一般的な用途であれば十分使用可能)

推奨スライサー設定（水漏れ防止）:
    - 壁ループ (Wall Loops): 3〜4回
    - 底面レイヤー (Bottom Shell Layers): 4〜5層
    - インフィル: 15-20% (Grid or Gyroid)
    - 壁ジェネレーター (Wall generator): Arachne (壁の隙間を埋めるのに有効)

印刷統計（予想）:
    - pot_saucer: 印刷時間 約45分、フィラメント使用量 約25g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# パラメーター設定
POT_DIAMETER_BOTTOM = 100.0  # 鉢の底面外径
CLEARANCE = 4.0             # 片側のクリアランス
INNER_DIAMETER = POT_DIAMETER_BOTTOM + (CLEARANCE * 2)  # 108mm
WALL_THICKNESS = 2.5        # 壁の厚み
BOTTOM_THICKNESS = 2.5      # 底面の厚み
HEIGHT = 12.0               # 全体の高さ
RIB_HEIGHT = 1.2            # 底面リブの高さ
FILLET_RADIUS = 1.5         # 外側の角の丸み

# 出力パスの設定
OUTPUT_FILENAME = "pot_saucer.step"
current_dir = os.path.dirname(__file__)
output_path = os.path.join(current_dir, OUTPUT_FILENAME)

def create_saucer():
    outer_diameter = INNER_DIAMETER + (WALL_THICKNESS * 2)
    rib_width = 1.5
    max_rib_radius = (INNER_DIAMETER / 2) - 1.5
    rib_radii = [max_rib_radius * 0.5, max_rib_radius]

    with BuildPart() as saucer:
        # メインの器部分（外形）
        Cylinder(radius=outer_diameter / 2, height=HEIGHT, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # 中をくり抜く
        with Locations((0, 0, BOTTOM_THICKNESS)):
            Cylinder(radius=INNER_DIAMETER / 2, height=HEIGHT - BOTTOM_THICKNESS, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # 底面のリブ（通気・水はけ用）
        for r in rib_radii:
            with BuildSketch(Location((0, 0, BOTTOM_THICKNESS))):
                Circle(radius=r)
                Circle(radius=r - rib_width, mode=Mode.SUBTRACT)
            extrude(amount=RIB_HEIGHT)

        # 仕上げ: 角を丸める
        # 外側底面のエッジ
        bottom_outer_edge = saucer.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0].sort_by(SortBy.RADIUS)[-1]
        fillet(bottom_outer_edge, radius=FILLET_RADIUS)

        # 外側上端のエッジ
        top_outer_edge = saucer.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1].sort_by(SortBy.RADIUS)[-1]
        fillet(top_outer_edge, radius=0.5)

    return saucer.part

# モデル生成
result = create_saucer()

# STEPファイルへのエクスポート
print(f"Exporting to {output_path}...")
show_object(result)
export_step(result, output_path)
print("Done.")
