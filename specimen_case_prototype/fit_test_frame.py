"""
標本ケース アクリル落とし込み・着脱性確認用 薄型テストフレーム (Fit Test Frame)

【目的】
アクリル板の落とし込み具合（四隅ピン角逃げ、バキューム吸着解消、隠し指抜きノッチの使い勝手、磁石・蓋との嵌合）を、
フィラメント消費と印刷時間を最小限に抑えて素早くテスト・確認するための「底なし・薄型テストフレーム」モデルです。

【主な特徴】
1. 薄型設計: 総高さ 10.20mm (0.30mm レイヤー × 34層)
   - ポケット深さ 5.10mm (17層) + 下部受け棚 5.10mm (17層)
2. 底なし貫通: 標本空間は底板がなく完全スルー。材料わずか約15g、印刷時間約15〜20分で出力可能。
3. 本番完全互換:
   - ポケット四隅のピン角逃げ ＆ 空気抜き (ドッグボーン R1.2mm)
   - 隠し指抜きノッチ (長辺中央左右、幅18mm × 外側3mm × 深さ6mm)
   - 四隅磁石穴 (φ6.4mm × 深さ1.8mm)
4. 将来のサイズ変更対応:
   - ACRYLIC_WIDTH, ACRYLIC_LENGTH, POCKET_CLEARANCE_XY を変更することで、20cm四方等の大型テストフレームも即座に生成可能。
"""

import math
from pathlib import Path
from build123d import *


# ==============================================================================
# 設計パラメーター
# ==============================================================================

LAYER_HEIGHT = 0.30         # 0.6mm ノズル黄金比の積層ピッチ

# --- アクリルプレート寸法 (実測値) ---
# 小型試作: 76.0mm × 127.0mm × 5.0mm
# (将来の20cm版テスト時はここを 200.0, 200.0, 5.0、CLEARANCEを 0.8 に変更)
ACRYLIC_WIDTH = 76.0
ACRYLIC_LENGTH = 127.0
ACRYLIC_THICKNESS = 5.0

# --- 公差（クリアランス） ---
# 小型試作: 0.4mm (片側 0.2mm)
# 20cm大型化時: 0.8mm (片側 0.4mm)
POCKET_CLEARANCE_XY = 0.4

# --- ケース基本構造 ---
SHELF_WIDTH = 1.8           # アクリル板を受ける棚の幅 (1.8mm)
CORNER_RADIUS = 3.0         # 外郭四隅フィレット半径

# --- アクリル着脱機構 ---
CORNER_RELIEF_R = 1.2       # 四隅ピン角逃げ ＆ 空気抜き円筒半径 (1.2mm)
NOTCH_W = 3.0               # 指抜きノッチ外側への掘り込み量 (3.0mm)
NOTCH_L = 18.0              # 指抜きノッチ長さ (18.0mm)
NOTCH_DEPTH = 6.0           # 指抜きノッチ深さ (6.0mm)

# --- ネオジム磁石 ---
MAGNET_HOLE_D = 6.4         # 磁石穴直径 (φ6.0mm用公差+0.4mm)
MAGNET_HOLE_DEPTH = 6 * LAYER_HEIGHT  # 1.80mm (6層)

# ==============================================================================
# 派生寸法の計算 (0.30mm レイヤー完全整合)
# ==============================================================================

# アクリルポケット寸法
POCKET_W = ACRYLIC_WIDTH + POCKET_CLEARANCE_XY      # 76.4mm
POCKET_L = ACRYLIC_LENGTH + POCKET_CLEARANCE_XY    # 127.4mm
POCKET_DEPTH = 17 * LAYER_HEIGHT                    # 5.10mm (17層)

# アクリル受け棚の下部フレーム高さ
FRAME_BASE_H = 17 * LAYER_HEIGHT                    # 5.10mm (17層)

# テストフレーム総高さ
TOTAL_H = FRAME_BASE_H + POCKET_DEPTH               # 10.20mm (34層)

# 貫通内寸（底なし開口部）
INNER_W = POCKET_W - 2 * SHELF_WIDTH                # 72.8mm
INNER_L = POCKET_L - 2 * SHELF_WIDTH                # 123.8mm

# 磁石中心座標 (本番と完全一致)
diag_dist = 1.0 + (MAGNET_HOLE_D / 2)
diag_offset = diag_dist / math.sqrt(2)
MAG_CX = (POCKET_W / 2) + diag_offset               # 41.17mm
MAG_CY = (POCKET_L / 2) + diag_offset               # 66.67mm

# 外形寸法 (本番と完全一致)
TOTAL_W = 91.2
TOTAL_L = 142.2

# 各高さ基準 (Z座標)
Z_BOTTOM = 0.0
Z_SHELF = FRAME_BASE_H                              # 5.10mm
Z_TOP = TOTAL_H                                     # 10.20mm


def create_base_sketch() -> Sketch:
    """角丸外郭プロファイルを作成します。"""
    with BuildSketch() as sk:
        r = Rectangle(TOTAL_W, TOTAL_L)
        fillet(r.vertices(), radius=CORNER_RADIUS)
    return sk.sketch


def build_fit_test_frame() -> Part:
    """
    底なし薄型テストフレームを生成します。
    """
    base_sk = create_base_sketch()

    with BuildPart() as frame:
        # 1. 外郭ソリッドの押し出し (高さ 10.20mm)
        extrude(base_sk, amount=TOTAL_H)

        # 2. 内寸の底なし完全貫通 (Z=0 から天面まで突き抜け)
        with Locations((0, 0, -1.0)):
            Box(
                INNER_W,
                INNER_L,
                TOTAL_H + 2.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 3. アクリル落とし込みポケットを削る (Z=Z_SHELF 5.10mm から天面まで)
        with Locations((0, 0, Z_SHELF)):
            Box(
                POCKET_W,
                POCKET_L,
                POCKET_DEPTH + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 4. 四隅のピン角逃げ ＆ 空気抜き (ドッグボーン R1.2mm)
        pocket_corners = [
            (POCKET_W / 2, POCKET_L / 2),
            (-POCKET_W / 2, POCKET_L / 2),
            (-POCKET_W / 2, -POCKET_L / 2),
            (POCKET_W / 2, -POCKET_L / 2)
        ]
        for cx, cy in pocket_corners:
            with Locations((cx, cy, Z_SHELF)):
                Cylinder(
                    radius=CORNER_RELIEF_R,
                    height=POCKET_DEPTH + 1.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT
                )

        # 5. 天面四隅の磁石ポケット (深さ 1.80mm = 6層)
        corner_locs = [
            (MAG_CX, MAG_CY, Z_TOP),
            (-MAG_CX, MAG_CY, Z_TOP),
            (-MAG_CX, -MAG_CY, Z_TOP),
            (MAG_CX, -MAG_CY, Z_TOP)
        ]
        for loc in corner_locs:
            with Locations(loc):
                Cylinder(
                    radius=MAGNET_HOLE_D / 2,
                    height=MAGNET_HOLE_DEPTH,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                    mode=Mode.SUBTRACT
                )

        # 6. 隠し指抜きノッチ (長辺中央左右、幅18mm × 外側3mm × 深さ6mm)
        notch_locs = [
            (POCKET_W / 2, 0, Z_TOP),
            (-POCKET_W / 2, 0, Z_TOP)
        ]
        for nx, ny, nz in notch_locs:
            with Locations((nx, ny, nz)):
                Box(
                    NOTCH_W * 2,
                    NOTCH_L,
                    NOTCH_DEPTH,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                    mode=Mode.SUBTRACT
                )

    return frame.part


def main():
    print("=" * 60)
    print("標本ケース アクリル落とし込み用 薄型テストフレーム生成")
    print("=" * 60)
    print(f"・積層ピッチ: {LAYER_HEIGHT} mm")
    print(f"・フレーム総高さ: {TOTAL_H:.2f} mm ({int(round(TOTAL_H / LAYER_HEIGHT))} 層)")
    print(f"・ポケット深さ: {POCKET_DEPTH:.2f} mm ({int(round(POCKET_DEPTH / LAYER_HEIGHT))} 層)")
    print(f"・下部棚高: {FRAME_BASE_H:.2f} mm ({int(round(FRAME_BASE_H / LAYER_HEIGHT))} 層)")
    print(f"・ポケット内寸: {POCKET_W:.2f} mm × {POCKET_L:.2f} mm (クリアランス +{POCKET_CLEARANCE_XY}mm)")
    print(f"・貫通内寸 (底なし): {INNER_W:.2f} mm × {INNER_L:.2f} mm")
    print(f"・四隅逃げR: {CORNER_RELIEF_R} mm (ドッグボーン)")
    print(f"・指抜きノッチ: 幅 {NOTCH_L} mm × 外側 {NOTCH_W} mm × 深さ {NOTCH_DEPTH} mm")
    print(f"・磁石穴: φ{MAGNET_HOLE_D} mm × 深さ {MAGNET_HOLE_DEPTH:.2f} mm")

    frame = build_fit_test_frame()

    # 出力パス設定
    output_dir = Path(__file__).resolve().parent
    step_path = output_dir / "fit_test_frame.step"

    print(f"\nSTEPファイル出力中: {step_path.name}")
    export_step(frame, str(step_path))
    print(f"出力完了: {step_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
