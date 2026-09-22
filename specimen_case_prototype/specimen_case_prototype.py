"""
標本ケースプロトタイプ (specimen_case_prototype)
Bambu Lab P2S / PETG-CF 専用 最高級ソリッド・モノリス 昆虫標本ケース
【新世代アーキテクチャ: 蓋側アクリル落とし込み構造】

設計コンセプト (First Principles / ゼロベース設計):
  1. 【公差リスクの完全局所化】
     - アクリル落とし込みポケットを「本体」から「蓋（トップフレーム）」裏面へ移設。
     - アクリル寸法の誤差や熱収縮のリスクを、軽量な蓋（約28g / 25分）だけに閉じ込め、
       重い本体（約100g / 1.5時間、20cm版なら400g超）は100%安全にそのまま使用可能。
  2. 【着脱性の飛躍的向上（指抜きノッチの完全不要化）】
     - 表側の窓（開口部）からアクリル板を指でポンと押せるため、どれだけジャストフィットでも一瞬で外せる。
     - これにより、指抜きノッチを完全廃止し、内外ともにノイズゼロの完全ミニマルデザインへ昇華。
  3. 【日常操作の1アクション化】
     - 「アクリル板を抱えた蓋」をパカッと持ち上げるだけでケースが開閉可能（本物の標本箱感覚）。
     - アクリル板自体を直接触らないため、指紋や汚れがつかない。
  4. 【0.30mm レイヤー完全整合設計】
     - 0.6mm ノズルの黄金比 (0.30mm) に全Z寸法を完全統一。
     - 本体総高さ: 46.50mm (155層)
     - 蓋総厚み: 7.80mm (26層)
     - セット全体総高さ: 54.30mm (181層、従来と完全一致)
     - 標本有効深さ: 40.00mm (発泡ボード5.0mm敷設後)
  5. 【サポート完全ゼロ ＆ ワンプレート印刷】
     - 本体・蓋ともにオーバーハングゼロでサポート材一切不要。
     - 蓋は美しい額縁天面を下にしてベッドに接地して印刷するため、表面性状も最高品質。

推奨フィラメント & ノズル:
    - フィラメント: Bambu PETG-CF 黒 (Black)
    - ノズル: 0.6mm タングステンノズル (または硬化鋼ノズル)

推奨スライサー設定 (Bambu Studio):
    - ノズル径: 0.6mm
    - レイヤー高さ: 0.30mm Standard (全高さが0.30mmの完全整数倍)
    - 初期レイヤー高さ: 0.30mm
    - 壁ループ (Wall Loops): 2 (外壁約1.24mmで高剛性)
    - トップシェル / ボトムシェル: 各3層 (0.90mm)
    - 疎らインフィル: 10% Cross Hatch
    - サポート: なし (None)
    - 円弧フィッティング (Arc fitting): 有効 (Enable)
"""

import math
import os
from pathlib import Path
from build123d import *

# ==============================================================================
# 基本パラメーター (単位: mm)
# ==============================================================================

# --- レイヤー高さ基準 ---
LAYER_HEIGHT = 0.30         # 0.6mmノズルの黄金比 (50%)

# --- アクリルプレート実寸 ---
# 小型試作: 76.0mm × 127.0mm × 5.0mm
# (将来の20cm版時はここを 200.0, 200.0, 5.0、CLEARANCEを 0.8 に変更するだけで完全追従)
ACRYLIC_WIDTH = 76.0        # 短辺 (X方向)
ACRYLIC_LENGTH = 127.0      # 長辺 (Y方向)
ACRYLIC_THICKNESS = 5.0     # 厚み (Z方向)

# --- 公差（クリアランス） ---
# 小型試作: 0.4mm (片側 0.2mm)
# 20cm大型化時: 0.8mm (片側 0.4mm)
POCKET_CLEARANCE_XY = 0.4

# --- 標本内部空間 ---
# 0.30mm × 150層 = 45.00mm (発泡ボード5.0mm + 標本深さ40.0mm)
INNER_DEPTH = 150 * LAYER_HEIGHT
SHELF_WIDTH = 1.8           # 額縁押さえ幅 (四辺均等1.8mmでアクリルをホールド、かかり代1.6mm)

# --- ケース基本構造 ---
# 0.30mm × 5層 = 1.50mm (底板厚み)
BOTTOM_THICKNESS = 5 * LAYER_HEIGHT

# 蓋の天面額縁厚み: 0.30mm × 9層 = 2.70mm
LID_FRAME_THICKNESS = 9 * LAYER_HEIGHT
CORNER_RADIUS = 3.0         # 外郭四隅フィレット半径

# --- アクリル着脱機構（蓋側） ---
# 0.6mmノズル内角R（約0.35mm）への噛み込みを防ぐ最小かつ十分な逃げ半径
CORNER_RELIEF_R = 0.6       # 0.6mm (ノズル半径と同等、磁石穴との隔壁を0.4mm確保)

# --- ネオジム磁石 (実寸 φ6.0mm × 1.5mm) ---
MAGNET_DIAMETER = 6.0       # 磁石直径
MAGNET_THICKNESS = 1.5      # 磁石厚み
MAGNET_HOLE_D = 6.4         # 磁石穴直径 (0.6mmノズル収縮マージン+接着剤逃げしろ)
# 0.30mm × 6層 = 1.80mm (接着剤膜厚+約0.3mmの確実な沈み込みマージン)
MAGNET_HOLE_DEPTH = 6 * LAYER_HEIGHT

# --- 壁厚マージン (0.6mm ノズル壁ループ2本 = 約1.24mm に最適化) ---
CORNER_INNER_WALL = 1.0     # アクリル角と磁石穴の間の内側隔壁
OUTER_WALL_MARGIN = 1.23    # 磁石穴外側からケース外周までの肉厚

# ==============================================================================
# 計算される派生寸法 (First Principles / 完全パラメトリック連動)
# ==============================================================================

# アクリルポケット寸法（蓋裏面の掘り込み）
POCKET_W = ACRYLIC_WIDTH + POCKET_CLEARANCE_XY      # 76.4mm
POCKET_L = ACRYLIC_LENGTH + POCKET_CLEARANCE_XY    # 127.4mm
# 0.30mm × 17層 = 5.10mm (アクリル5.0mmに対して+0.10mmマージンで確実にツライチ以下に収まる)
POCKET_DEPTH = 17 * LAYER_HEIGHT

# 標本空間・窓の内寸（開口部）
INNER_W = POCKET_W - 2 * SHELF_WIDTH                # 72.8mm
INNER_L = POCKET_L - 2 * SHELF_WIDTH                # 123.8mm

# 磁石中心座標 (cx, cy)
diag_dist = CORNER_INNER_WALL + (MAGNET_HOLE_D / 2) # 1.0 + 3.2 = 4.2mm
diag_offset = diag_dist / math.sqrt(2)              # 約 2.97mm
MAG_CX = (POCKET_W / 2) + diag_offset               # 41.17mm
MAG_CY = (POCKET_L / 2) + diag_offset               # 66.67mm

# 外形寸法（磁石外側肉厚 1.23mm から数学的に完全自動導出）
TOTAL_W = 2 * (MAG_CX + (MAGNET_HOLE_D / 2) + OUTER_WALL_MARGIN)  # 91.20mm
TOTAL_L = 2 * (MAG_CY + (MAGNET_HOLE_D / 2) + OUTER_WALL_MARGIN)  # 142.20mm

# ケース本体の総高さ (0.30mm × 155層 = 46.50mm)
BODY_TOTAL_H = BOTTOM_THICKNESS + INNER_DEPTH

# 蓋の総厚み (0.30mm × 26層 = 7.80mm)
LID_TOTAL_H = LID_FRAME_THICKNESS + POCKET_DEPTH

# セット全体の総高さ (0.30mm × 181層 = 54.30mm、従来と完全一致)
SET_TOTAL_H = BODY_TOTAL_H + LID_TOTAL_H


def create_base_sketch() -> Sketch:
    """
    一切の突起・耳・くびれのない、角丸（R3.0mm）完全フラット長方形プロファイルを作成します。
    """
    with BuildSketch() as sk:
        r = Rectangle(TOTAL_W, TOTAL_L)
        fillet(r.vertices(), radius=CORNER_RADIUS)
    return sk.sketch


def build_case_body() -> Part:
    """
    標本ケース本体（case_body）を生成します。
    完全フラット直方体・全Z寸法0.30mmレイヤー完全整合。
    総高さ 46.50mm (155層)。
    内寸 72.8mm × 123.8mm × 深さ 45.00mm。
    天面四隅に磁石ポケット（深さ 1.80mm = 6層）。
    ポケットやノッチ、段差のない、極限に美しくストレートなソリッドボックス。
    """
    base_sk = create_base_sketch()

    with BuildPart() as case:
        # 1. 外郭ソリッドの押し出し（高さ 46.50mm）
        extrude(base_sk, amount=BODY_TOTAL_H)

        # 2. 標本＆発泡ボードの内部空間を削る（Z=1.50 から天面まで貫通 72.8mm × 123.8mm）
        with Locations((0, 0, BOTTOM_THICKNESS)):
            Box(
                INNER_W,
                INNER_L,
                BODY_TOTAL_H - BOTTOM_THICKNESS + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 3. 天面四隅の磁石ポケットを削る（深さ 1.80mm = 6層）
        corner_locs = [
            (MAG_CX, MAG_CY, BODY_TOTAL_H),
            (-MAG_CX, MAG_CY, BODY_TOTAL_H),
            (-MAG_CX, -MAG_CY, BODY_TOTAL_H),
            (MAG_CX, -MAG_CY, BODY_TOTAL_H)
        ]
        for loc in corner_locs:
            with Locations(loc):
                Cylinder(
                    radius=MAGNET_HOLE_D / 2,
                    height=MAGNET_HOLE_DEPTH,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                    mode=Mode.SUBTRACT
                )

    return case.part


def build_top_frame() -> Part:
    """
    新アーキテクチャの蓋（top_frame）を生成します。
    【印刷向き】額縁の天面をZ=0（ビルドプレート側）にして配置。
    表面テクスチャが美しく仕上がり、サポート材完全ゼロで成形可能。

    Z構成:
      - Z=0.00 〜 2.70mm: 天面額縁（9層、中央開口 72.8×123.8mm）
      - Z=2.70 〜 7.80mm: アクリルポケット（17層、開口 76.4×127.4mm）
      - Z=7.80mm (上面): 本体との合わせ面。四隅に磁石穴（深さ1.80mm）
    """
    base_sk = create_base_sketch()

    with BuildPart() as frame:
        # 1. 外郭ソリッド押し出し（総厚み 7.80mm）
        extrude(base_sk, amount=LID_TOTAL_H)

        # 2. 中央の窓開口部を【上下完全貫通】して削る (72.8mm × 123.8mm)
        with Locations((0, 0, -1.0)):
            Box(
                INNER_W,
                INNER_L,
                LID_TOTAL_H + 2.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 3. アクリル落とし込みポケットを削る (Z=2.70mm から天面まで深さ 5.10mm)
        with Locations((0, 0, LID_FRAME_THICKNESS)):
            Box(
                POCKET_W,
                POCKET_L,
                POCKET_DEPTH + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 4. ポケット四隅のピン角逃げ (R0.6mm)
        # ※Z=2.70mm から天面まで削る（表の額縁には影響せず、磁石穴との隔壁0.4mmを健全に維持）
        pocket_corners = [
            (POCKET_W / 2, POCKET_L / 2),
            (-POCKET_W / 2, POCKET_L / 2),
            (-POCKET_W / 2, -POCKET_L / 2),
            (POCKET_W / 2, -POCKET_L / 2)
        ]
        for cx, cy in pocket_corners:
            with Locations((cx, cy, LID_FRAME_THICKNESS)):
                Cylinder(
                    radius=CORNER_RELIEF_R,
                    height=POCKET_DEPTH + 1.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT
                )

        # 5. 上面（本体との合わせ面 Z=7.80mm）四隅の磁石ポケットを削る (深さ 1.80mm = 6層)
        corner_locs = [
            (MAG_CX, MAG_CY, LID_TOTAL_H),
            (-MAG_CX, MAG_CY, LID_TOTAL_H),
            (-MAG_CX, -MAG_CY, LID_TOTAL_H),
            (MAG_CX, -MAG_CY, LID_TOTAL_H)
        ]
        for loc in corner_locs:
            with Locations(loc):
                Cylinder(
                    radius=MAGNET_HOLE_D / 2,
                    height=MAGNET_HOLE_DEPTH,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                    mode=Mode.SUBTRACT
                )

    return frame.part


# ==============================================================================
# 実行とエクスポート
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("標本ケース (蓋側アクリル落とし込み・新アーキテクチャ) 生成")
    print("=" * 60)
    case_body = build_case_body()
    top_frame = build_top_frame()

    print(f"・本体寸法: {case_body.bounding_box().size.X:.1f} × {case_body.bounding_box().size.Y:.1f} × {case_body.bounding_box().size.Z:.2f} mm")
    print(f"・蓋寸法:   {top_frame.bounding_box().size.X:.1f} × {top_frame.bounding_box().size.Y:.1f} × {top_frame.bounding_box().size.Z:.2f} mm")
    print(f"・本体ソリッド体積: {case_body.volume / 1000.0:.2f} cm3 (概算重量 約100g)")
    print(f"・蓋ソリッド体積:   {top_frame.volume / 1000.0:.2f} cm3 (概算重量 約28g)")
    print(f"・セット総高さ:     {BODY_TOTAL_H + LID_TOTAL_H:.2f} mm (181層)")
    print(f"・アクリルポケット: 蓋裏面に配置 ({POCKET_W:.2f} × {POCKET_L:.2f} × 深さ {POCKET_DEPTH:.2f} mm)")
    print(f"・四隅逃げR:        {CORNER_RELIEF_R:.1f} mm (磁石穴との隔壁 0.40mm 確保)")
    print(f"・指抜きノッチ:     完全廃止（窓側からワンプッシュで着脱可能）")

    # アセンブリ配置: ワンプレート印刷
    # 本体の右側にトップフレームを並べて配置（Z=0接地）
    placed_frame = top_frame.moved(Location((TOTAL_W + 16.0, 0, 0)))
    assembly = Compound(children=[case_body, placed_frame])

    output_dir = os.path.dirname(__file__)
    main_step_path = os.path.join(output_dir, "specimen_case_prototype.step")

    # 本番モデル (本体 + 蓋のワンプレート配置)
    export_step(assembly, main_step_path)
    print(f"\nSuccessfully exported Main STEP to: {main_step_path}")

    # 蓋単体テスト用モデル (アクリル嵌合確認用として単体出力も保持)
    test_step_path = os.path.join(output_dir, "fit_test_frame.step")
    export_step(top_frame, test_step_path)
    print(f"Successfully exported Lid Fit Test STEP to: {test_step_path}")
    print("=" * 60)

    try:
        from ocp_vscode import show, Camera
        show(case_body, placed_frame, names=["case_body", "top_frame"], reset_camera=Camera.RESET)
        print("OCP CAD Viewer にモデルを転送しました！")
    except Exception as e:
        try:
            from ocp_vscode import show_object
            show_object(case_body, name="case_body")
            show_object(placed_frame, name="top_frame")
            print("OCP CAD Viewer (show_object) にモデルを転送しました！")
        except Exception as e2:
            print(f"OCP CAD Viewer 表示スキップ: {e2}")
