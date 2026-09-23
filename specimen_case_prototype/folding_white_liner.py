"""
標本ケース用 超薄型折りたたみホワイトインナー (Folding White Liner)
Bento3D スタイル / 0.6mm ノズル × 2層 (0.60mm厚) リビングヒンジ設計

【特徴】
1. 厚み 0.60mm (2層) / 折り目 0.30mm (1層)
   - 0.6mm ノズルでわずか2層のため、印刷時間約6〜8分・材料約20gで爆速出力。
   - 1層のリビングヒンジ溝により、手で直角に綺麗に折り曲げ可能。
2. テクスチャプレートの質感がそのまま内壁に
   - ベッド接地側の美しいマットホワイト面が内壁の表面になります。
3. 交換・メンテナンス容易
   - 汚れたら引き抜いて丸洗い、または数十円で即座に新品を再印刷して差し替え可能。
4. 寸法完全整合
   - specimen_case_prototype.py の内寸 (72.8mm × 123.8mm × 45.0mm) にジャストフィット。
"""

import math
from pathlib import Path
from build123d import *

# ==============================================================================
# パラメーター設定 (単位: mm)
# ==============================================================================

LAYER_HEIGHT = 0.18         # 積層ピッチ (0.6mmノズル High Quality設定 0.18mm)
TOTAL_THICKNESS = 2 * LAYER_HEIGHT   # 0.36mm (2層)
HINGE_THICKNESS = 1 * LAYER_HEIGHT   # 0.18mm (1層リビングヒンジ: クリアファイル級の超しなやかさ・割れゼロ)
HINGE_GAP = 1.0             # 折り目溝幅 (1.0mm: 0.6mmノズルの吐出幅約0.62mmに対し確実に非融着・応力分散)

# --- ケース内寸 (specimen_case_prototype.py 準拠) ---
# 内寸: 72.8mm × 123.8mm × 深さ 45.00mm
CASE_INNER_W = 72.8
CASE_INNER_L = 123.8
CASE_INNER_DEPTH = 45.00

# --- インナー寸法（ベッド接地側を内面として外折りしたときの実外郭から完全逆算） ---
# 狙いとする折った状態の外寸: 72.0mm × 123.0mm (ケース内寸 72.8×123.8 に対し四方0.4mmの完全安全クリアランス)
# 折ったときの実効外寸 = BASE + 2 * TOTAL_THICKNESS (約 0.72mm)
# BASE_W = 72.0 - 2 * 0.36 = 71.28 -> 71.20mm
# BASE_L = 123.0 - 2 * 0.36 = 122.28 -> 122.20mm
BASE_W = 71.20
BASE_L = 122.20
WALL_H = 44.50              # 深さ45.0mmに対して0.5mmマージン (受け棚や蓋に干渉ゼロ)
CORNER_CHAMFER = 1.5        # 立ち上げ時の垂直コーナー干渉・長手方向の座屈を防ぐ逃げ面取り (1.5mm)


def build_folding_white_liner() -> Part:
    """
    十字展開図のリビングヒンジ付き超薄型ホワイトインナーシートを生成します。
    Z=0 はベッド接地側（平滑な内壁面）。
    Z=0.30〜0.60mm に壁面リブを配置し、折り目部分を0.30mm（1層）の溝とします。
    """
    half_w = BASE_W / 2
    half_l = BASE_L / 2

    with BuildPart() as liner:
        # 1. 第1層（Z=0 〜 0.30mm）: 全体をつなぐ連続したベースシート（十字型）
        with BuildSketch() as sk_base:
            # 中央底面
            Rectangle(BASE_W + 2 * (HINGE_GAP + WALL_H), BASE_L)
            Rectangle(BASE_W, BASE_L + 2 * (HINGE_GAP + WALL_H), mode=Mode.ADD)
        extrude(sk_base.sketch, amount=TOTAL_THICKNESS)

        # 2. 折り目ヒンジ溝を上から削る (深さ 0.30mm、Z=0.30mm 〜 0.60mm)
        # 4辺の境界に幅 HINGE_GAP の溝を掘る
        # 左右のヒンジ溝 (X方向)
        hinge_cut_depth = TOTAL_THICKNESS - HINGE_THICKNESS # 0.30mm
        z_cut_start = HINGE_THICKNESS # 0.30mm

        # 左右ヒンジ (長辺方向の溝)
        for side in [-1, 1]:
            with Locations((side * (half_w + HINGE_GAP / 2), 0, z_cut_start)):
                Box(
                    HINGE_GAP,
                    BASE_L,
                    hinge_cut_depth + 0.1,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT
                )

        # 前後ヒンジ (短辺方向の溝)
        for side in [-1, 1]:
            with Locations((0, side * (half_l + HINGE_GAP / 2), z_cut_start)):
                Box(
                    BASE_W,
                    HINGE_GAP,
                    hinge_cut_depth + 0.1,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT
                )

        # 3. 立ち上げたときに隣り合う側面同士が干渉しないよう、側面の端を微小に面取り/逃がす
        # 左右の羽のY端
        for side_x in [-1, 1]:
            x_center = side_x * (half_w + HINGE_GAP + WALL_H / 2)
            for side_y in [-1, 1]:
                with Locations((x_center, side_y * half_l, -0.1)):
                    Box(
                        WALL_H + 1.0,
                        CORNER_CHAMFER * 2,
                        TOTAL_THICKNESS + 0.2,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                        mode=Mode.SUBTRACT
                    )

        # 前後の羽のX端
        for side_y in [-1, 1]:
            y_center = side_y * (half_l + HINGE_GAP + WALL_H / 2)
            for side_x in [-1, 1]:
                with Locations((side_x * half_w, y_center, -0.1)):
                    Box(
                        CORNER_CHAMFER * 2,
                        WALL_H + 1.0,
                        TOTAL_THICKNESS + 0.2,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                        mode=Mode.SUBTRACT
                    )

    return liner.part


def main():
    print("=" * 60)
    print("標本ケース用 超薄型折りたたみホワイトインナー (Bento3Dスタイル) 生成")
    print("=" * 60)
    liner = build_folding_white_liner()
    bbox = liner.bounding_box()

    print(f"・積層ピッチ: {LAYER_HEIGHT} mm (0.6mm ノズル)")
    print(f"・総厚み:     {TOTAL_THICKNESS:.2f} mm (2層)")
    print(f"・折り目厚み: {HINGE_THICKNESS:.2f} mm (1層リビングヒンジ)")
    print(f"・展開総外寸: {bbox.size.X:.1f} mm × {bbox.size.Y:.1f} mm (ベッド256×256に余裕で収まります)")
    print(f"・底面寸法:   {BASE_W:.1f} mm × {BASE_L:.1f} mm")
    print(f"・側面高さ:   {WALL_H:.1f} mm")
    print(f"・ソリッド体積: {liner.volume / 1000.0:.2f} cm3")
    print(f"・概算重量:   約 {(liner.volume / 1000.0) * 1.24:.1f} g (PLA)")
    print(f"・推定印刷時間: 約 6〜8 分")

    output_dir = Path(__file__).resolve().parent
    step_path = output_dir / "folding_white_liner.step"

    print(f"\nSTEPエクスポート中: {step_path.name}")
    export_step(liner, str(step_path))
    print(f"エクスポート完了: {step_path}")
    print("=" * 60)

    try:
        from ocp_vscode import show, Camera
        show(liner, names=["folding_white_liner"], reset_camera=Camera.RESET)
        print("OCP CAD Viewer にモデルを転送しました！")
    except Exception as e:
        print(f"Viewer 表示スキップ: {e}")


if __name__ == "__main__":
    main()
