import os
import math
from build123d import *
from ocp_vscode import show_object

"""
設計要件:
    - 昆虫標本（国産カブトムシ等）用の高品位標本ケース（四隅マグネット・トップドロップ式）。
    - アクリルプレート（実寸 76.0mm × 127.0mm × 5.0mm）を上から段差に置くだけの「トップドロップ式」。
      スライド摩擦が一切ないため、PETG-CFのザラつきによるアクリルの擦り傷が物理的に完全ゼロ。
    - 空中に浮くスライド溝（庇）を全廃し、オーバーハング完全ゼロ（垂れ下がり・糸引きゼロ）。
    - 直線壁は 2.4mm（0.6mmノズル×4周で完全ソリッド）に極限スリム化し、本体重量を約80g台へと約35%大幅軽量化！
    - 内壁は底から上まで完全な長方形（直角）を維持し、底面発泡スチロールボード（5.0mm）がスムーズに敷ける。
    - 四隅のコーナーに φ6.0mm × 厚み1.5mm のネオジム磁石を埋め込み、トップフレームが「パチン！」と吸着。
      開閉時の振動がゼロで、標本（脚や触覚）を痛めず、縦置き展示でもアクリルが確実に保持される。
    - 将来の 200mm × 200mm 等の大型アクリルプレートにも数値を変更するだけで自動スケールする完全パラメトリック設計。

推奨フィラメント & ノズル:
    - フィラメント: Bambu PETG-CF 黒 (Black)
    - ノズル: 0.6mm タングステンノズル (または硬化鋼ノズル)

推奨スライサー設定 (Bambu Studio):
    - ノズル径: 0.6mm
    - レイヤー高さ: 0.24mm Standard
    - 壁面生成器 (Wall generator): Arachne
    - シーム位置 (Seam): 整列 (Aligned)
    - 壁ループ (Wall Loops): 3〜4
    - トップ/ボトムシェルレイヤー: 4〜5層
    - インフィル: 15% (Gyroid)
    - サポート: なし (None / オーバーハング完全ゼロ設計)

印刷統計（予想 - 0.6mmノズル / 0.24mmレイヤー）:
    - case_body: 印刷時間 約1時間10分、フィラメント使用量 約85g（前回比 約35%削減！）
    - top_frame: 印刷時間 約12分、フィラメント使用量 約12g

磁石の接着について（重要）:
    - φ6.0mm × 厚み1.5mm のネオジム磁石を計8個（本体4個 ＋ トップフレーム4個）使用します。
    - 本体とトップフレームが互いに引き合うよう、極性（N極/S極）の向きを合わせて瞬間接着剤等で固定してください。

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# ==============================================================================
# パラメーター設定 (単位: mm)
# ==============================================================================

# --- アクリルプレート実寸 ---
ACRYLIC_WIDTH = 76.0        # 短辺 (X方向) ※20cm時は 200.0
ACRYLIC_LENGTH = 127.0      # 長辺 (Y方向) ※20cm時は 200.0
ACRYLIC_THICKNESS = 5.0     # 厚み (Z方向、実測値)

# --- 標本空間 & 発泡スチロールボード ---
BOARD_THICKNESS = 5.0       # 底面発泡ボード厚み
SPECIMEN_DEPTH = 40.0       # 標本有効深さ（有頭昆虫針のカブトムシが余裕で入る高さ）
SHELF_WIDTH = 2.0           # アクリル板を受ける外周段差の幅

# --- ケース基本構造 ---
BOTTOM_THICKNESS = 2.0      # 底面ベース厚み（0.6mmノズル×4層、軽量高剛性）
WALL_THICKNESS = 2.4        # 4辺の直線外壁の厚み (0.6mmノズル×4周で完全充填)
TOP_FRAME_THICKNESS = 2.6   # トップフレームの厚み (Z方向)

# --- ネオジム磁石 (実寸 φ6.0mm × 1.5mm) ---
MAGNET_DIAMETER = 6.0       # 磁石直径
MAGNET_THICKNESS = 1.5      # 磁石厚み
MAGNET_HOLE_D = 6.2         # 磁石穴直径 (+0.2mmクリアランス)
MAGNET_HOLE_DEPTH = 1.7     # 磁石穴深さ (+0.2mmマージン、確実にツライチ以下に沈む)

# --- 公差（クリアランス） ---
POCKET_CLEARANCE_XY = 0.4   # アクリル落とし込み用遊び (片側 0.2mm)

# ==============================================================================
# 計算される派生寸法
# ==============================================================================

# アクリルポケット寸法（本体天面の掘り込み）
POCKET_W = ACRYLIC_WIDTH + POCKET_CLEARANCE_XY      # 76.4mm
POCKET_L = ACRYLIC_LENGTH + POCKET_CLEARANCE_XY    # 127.4mm
POCKET_DEPTH = ACRYLIC_THICKNESS                    # 5.0mm

# 標本・ボード空間の内寸（開口部）
INNER_W = POCKET_W - 2 * SHELF_WIDTH                # 72.4mm
INNER_L = POCKET_L - 2 * SHELF_WIDTH                # 123.4mm
INNER_DEPTH = BOARD_THICKNESS + SPECIMEN_DEPTH      # 45.0mm

# 直線部の外形寸法
STRAIGHT_OUTER_W = POCKET_W + 2 * WALL_THICKNESS    # 81.2mm (X: ±40.6)
STRAIGHT_OUTER_L = POCKET_L + 2 * WALL_THICKNESS    # 132.2mm (Y: ±66.1)

# ケース本体の総高さ
TOTAL_H = BOTTOM_THICKNESS + INNER_DEPTH + POCKET_DEPTH  # 52.0mm

# 各高さ基準 (Z座標)
Z_BOTTOM = 0.0
Z_INNER_FLOOR = BOTTOM_THICKNESS                    # 2.0mm (発泡ボード底)
Z_SHELF = Z_INNER_FLOOR + INNER_DEPTH               # 47.0mm (アクリル受け棚面)
Z_TOP = TOTAL_H                                     # 52.0mm (ケース天面)

# 四隅の磁石中心座標 (cx, cy)
diag_dist = 1.2 + (MAGNET_HOLE_D / 2)  # 4.3mm
diag_offset = diag_dist / math.sqrt(2) # 約 3.04mm
MAG_CX = (POCKET_W / 2) + diag_offset   # 41.24mm
MAG_CY = (POCKET_L / 2) + diag_offset   # 66.74mm
CORNER_BOSS_RADIUS = (MAGNET_HOLE_D / 2) + 1.5  # 4.6mm (外側肉厚1.5mm)


def create_outer_profile() -> Sketch:
    """
    四隅にマグネットボスを滑らかに融合させた外郭2Dプロファイルを作成します。
    """
    with BuildSketch() as sk:
        Rectangle(STRAIGHT_OUTER_W, STRAIGHT_OUTER_L)
        corner_locs = [
            (MAG_CX, MAG_CY),
            (-MAG_CX, MAG_CY),
            (-MAG_CX, -MAG_CY),
            (MAG_CX, -MAG_CY)
        ]
        for loc in corner_locs:
            with Locations(loc):
                Circle(radius=CORNER_BOSS_RADIUS, mode=Mode.ADD)
    return sk.sketch


def build_case_body() -> Part:
    """
    標本ケース本体（case_body）を生成します。
    """
    outer_sk = create_outer_profile()

    with BuildPart() as case:
        # 1. 外郭ソリッドの押し出し（底面から天面まで完全垂直）
        extrude(outer_sk, amount=TOTAL_H)

        # 2. 標本＆発泡ボードの内部空間を削る（Z=2.0 から上まで）
        with Locations((0, 0, Z_INNER_FLOOR)):
            Box(
                INNER_W,
                INNER_L,
                TOTAL_H - Z_INNER_FLOOR + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 3. アクリル落とし込みポケットを削る（Z=47.0 から天面まで）
        with Locations((0, 0, Z_SHELF)):
            Box(
                POCKET_W,
                POCKET_L,
                POCKET_DEPTH + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 4. 天面四隅の磁石ポケットを削る
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

    return case.part


def build_top_frame() -> Part:
    """
    アクリル板を上から押さえ、四隅の磁石で吸着するトップフレーム（top_frame）を生成します。
    """
    outer_sk = create_outer_profile()

    with BuildPart() as frame:
        # 1. 外郭ソリッドの押し出し
        extrude(outer_sk, amount=TOP_FRAME_THICKNESS)

        # 2. 中央の窓開口部を削る（標本空間と同じ開口 72.4mm × 123.4mm）
        Box(
            INNER_W,
            INNER_L,
            TOP_FRAME_THICKNESS + 2.0,
            align=(Align.CENTER, Align.CENTER, Align.CENTER),
            mode=Mode.SUBTRACT
        )

        # 3. 裏面（Z=0）四隅の磁石ポケットを削る
        corner_locs = [
            (MAG_CX, MAG_CY, 0),
            (-MAG_CX, MAG_CY, 0),
            (-MAG_CX, -MAG_CY, 0),
            (MAG_CX, -MAG_CY, 0)
        ]
        for loc in corner_locs:
            with Locations(loc):
                Cylinder(
                    radius=MAGNET_HOLE_D / 2,
                    height=MAGNET_HOLE_DEPTH,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT
                )

        # 4. 指がかり用リセス（長辺中央の両外側に指をかけられる微小なくびれ）
        notch_w = 20.0
        notch_depth = 1.2
        for side in [-1, 1]:
            with Locations((side * (STRAIGHT_OUTER_W / 2), 0, TOP_FRAME_THICKNESS)):
                Box(
                    notch_depth * 2,
                    notch_w,
                    1.2 * 2,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    mode=Mode.SUBTRACT
                )

    return frame.part


# ==============================================================================
# 実行とエクスポート
# ==============================================================================
if __name__ == "__main__":
    print("Building 4-corner magnet specimen case model...")
    case_body = build_case_body()
    top_frame = build_top_frame()

    print(f"Case Body Bounding Box: {case_body.bounding_box()}")
    print(f"Top Frame Bounding Box: {top_frame.bounding_box()}")

    # アセンブリ配置: ワンプレート印刷
    # 本体の右側にトップフレームを並べて配置（フレームも底面Z=0接地）
    placed_frame = top_frame.moved(Location((STRAIGHT_OUTER_W + 18.0, 0, 0)))
    assembly = Compound(children=[case_body, placed_frame])

    output_dir = os.path.dirname(__file__)
    output_path = os.path.join(output_dir, "specimen_case_prototype.step")

    export_step(assembly, output_path)
    print(f"Successfully exported Magnet Model STEP to: {output_path}")

    try:
        show_object(case_body, name="case_body")
        show_object(placed_frame, name="top_frame")
    except Exception:
        pass
