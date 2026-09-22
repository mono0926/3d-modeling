import math
import os
from build123d import *
from ocp_vscode import show_object

"""
設計要件:
    - 昆虫標本（国産カブトムシ等）用の超軽量・高機能標本ケース。
    - monoさんの素晴らしい着想を採用：
      「本体は直線壁2.4mm＋四隅ミニ耳（ミッキーマウス耳）で約80g台の極限軽量化」、
      「蓋（トップフレーム）は完全な端正な直方体（長方形）で本体の耳をすっぽり覆うデザイン」。
    - 鑑賞時（上から見るとき）は端正な完全長方形の額縁のみが見え、本体の耳は影に隠れて気になりません。
    - 蓋のフチが本体直線壁に対して全周に約5.4mmの「美しい庇（ひさし）」となるため、
      どこからでも指先でスッと優しく開閉可能（開閉振動ゼロ、標本の脚・触角保護）。
    - アクリルプレート（実寸 76.0mm × 127.0mm × 5.0mm）を上からポンと置くだけの「トップドロップ式」。
      スライド摩擦が文字通りゼロのため、PETG-CFのザラつきによるアクリルの擦り傷が物理的に100%発生しない。
    - 天井庇を全廃し、オーバーハング完全ゼロ（垂れ下がり・糸引きゼロ、サポート材不要）。
    - 内壁は底から上まで完全な長方形（直角 72.4mm × 123.4mm）を維持し、発泡スチロールボード（5.0mm）が真上からストンと敷ける。
    - 四隅のφ6.0mm × 厚み1.5mm のネオジム磁石により「パチン！」と吸着。
    - トップフレームは中央窓が完全に上下貫通した額縁デザイン。
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
    - case_body: 印刷時間 約1時間05分、フィラメント使用量 約80g（超軽量・省フィラメント）
    - top_frame: 印刷時間 約12分、フィラメント使用量 約12g
    - 合計: 約92g（100g未満で大幅軽量・省資源！）

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
WALL_THICKNESS = 2.4        # 本体の直線外壁の厚み (0.6mmノズル×4周で超軽量・完全充填)
TOP_FRAME_THICKNESS = 2.8   # トップフレームの厚み (Z方向、磁石穴上部に1.1mmの頑丈な天面)
TOP_FRAME_CORNER_R = 3.0    # トップフレームの四隅フィレット半径

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

# 本体の直線部外形寸法
BODY_STRAIGHT_W = POCKET_W + 2 * WALL_THICKNESS     # 81.2mm (X: ±40.6)
BODY_STRAIGHT_L = POCKET_L + 2 * WALL_THICKNESS     # 132.2mm (Y: ±66.1)

# ケース本体の総高さ
TOTAL_H = BOTTOM_THICKNESS + INNER_DEPTH + POCKET_DEPTH  # 52.0mm

# 各高さ基準 (Z座標)
Z_BOTTOM = 0.0
Z_INNER_FLOOR = BOTTOM_THICKNESS                    # 2.0mm (発泡ボード底)
Z_SHELF = Z_INNER_FLOOR + INNER_DEPTH               # 47.0mm (アクリル受け棚面)
Z_TOP = TOTAL_H                                     # 52.0mm (ケース天面)

# 四隅の磁石中心座標 (cx, cy)
diag_dist = 1.2 + (MAGNET_HOLE_D / 2)               # 4.3mm
diag_offset = diag_dist / math.sqrt(2)              # 約 3.04mm
MAG_CX = (POCKET_W / 2) + diag_offset               # 41.24mm
MAG_CY = (POCKET_L / 2) + diag_offset               # 66.74mm
CORNER_BOSS_RADIUS = (MAGNET_HOLE_D / 2) + 1.5      # 4.6mm (外側肉厚1.5mm)

# トップフレームの外形寸法（耳の先端までカバーする端正な完全長方形）
FRAME_W = 92.0                                      # X: ±46.0mm (耳先端 45.84mm をすっぽり覆う)
FRAME_L = 143.0                                     # Y: ±71.5mm (耳先端 71.34mm をすっぽり覆う)


def build_case_body() -> Part:
    """
    本体（case_body）を生成します。
    直線部は厚さ2.4mmで超軽量、四隅にのみ磁石ボス（耳）を持つ高効率設計。
    """
    with BuildSketch() as sk:
        Rectangle(BODY_STRAIGHT_W, BODY_STRAIGHT_L)
        corner_locs = [
            (MAG_CX, MAG_CY),
            (-MAG_CX, MAG_CY),
            (-MAG_CX, -MAG_CY),
            (MAG_CX, -MAG_CY)
        ]
        for loc in corner_locs:
            with Locations(loc):
                Circle(radius=CORNER_BOSS_RADIUS, mode=Mode.ADD)
    outer_sk = sk.sketch

    with BuildPart() as case:
        # 1. 外郭ソリッドの押し出し（完全垂直）
        extrude(outer_sk, amount=TOTAL_H)

        # 2. 標本＆発泡ボードの内部空間を削る（Z=2.0 から上まで完全な長方形 72.4mm × 123.4mm）
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
        corner_locs_3d = [
            (MAG_CX, MAG_CY, Z_TOP),
            (-MAG_CX, MAG_CY, Z_TOP),
            (-MAG_CX, -MAG_CY, Z_TOP),
            (MAG_CX, -MAG_CY, Z_TOP)
        ]
        for loc in corner_locs_3d:
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
    蓋（top_frame）を生成します。
    美しい完全長方形（直方体・角丸R3mm）で、本体の耳を真上からすっぽり覆い隠します。
    """
    with BuildSketch() as sk:
        r = Rectangle(FRAME_W, FRAME_L)
        fillet(r.vertices(), radius=TOP_FRAME_CORNER_R)
    frame_sk = sk.sketch

    with BuildPart() as frame:
        # 1. 外郭ソリッドの押し出し
        extrude(frame_sk, amount=TOP_FRAME_THICKNESS)

        # 2. 中央の窓開口部を【完全に上下貫通】して削る（Z=-1.0 から削る）
        with Locations((0, 0, -1.0)):
            Box(
                INNER_W,
                INNER_L,
                TOP_FRAME_THICKNESS + 2.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 3. 裏面（下面 Z=0）四隅の磁石ポケットを削る（本体と完全同軸）
        corner_locs_3d = [
            (MAG_CX, MAG_CY, 0),
            (-MAG_CX, MAG_CY, 0),
            (-MAG_CX, -MAG_CY, 0),
            (MAG_CX, -MAG_CY, 0)
        ]
        for loc in corner_locs_3d:
            with Locations(loc):
                Cylinder(
                    radius=MAGNET_HOLE_D / 2,
                    height=MAGNET_HOLE_DEPTH,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT
                )

    return frame.part


# ==============================================================================
# 実行とエクスポート
# ==============================================================================
if __name__ == "__main__":
    print("Building Hybrid Specimen Case (Light Ear Body + Rectangular Top Frame)...")
    case_body = build_case_body()
    top_frame = build_top_frame()

    print(f"Case Body Bounding Box: {case_body.bounding_box()}")
    print(f"Top Frame Bounding Box: {top_frame.bounding_box()}")
    print(f"Case Body Volume: {case_body.volume / 1000.0:.2f} cm3")
    print(f"Top Frame Volume: {top_frame.volume / 1000.0:.2f} cm3")

    # アセンブリ配置: ワンプレート印刷
    # 本体の右側にトップフレームを並べて配置（Z=0接地）
    placed_frame = top_frame.moved(Location((105.0, 0, 0)))
    assembly = Compound(children=[case_body, placed_frame])

    output_dir = os.path.dirname(__file__)
    output_path = os.path.join(output_dir, "specimen_case_prototype.step")

    export_step(assembly, output_path)
    print(f"Successfully exported Hybrid STEP to: {output_path}")

    try:
        show_object(case_body, name="case_body")
        show_object(placed_frame, name="top_frame")
    except Exception:
        pass
