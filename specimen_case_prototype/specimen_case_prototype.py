import math
import os
from build123d import *
from ocp_vscode import show_object

"""
設計要件:
    - 昆虫標本（国産カブトムシ等）用の最高級・洗練されたオクタゴン・コーナー標本ケース。
    - 不格好な外出し円柱（耳）を全廃し、四隅を斜め45°に落とした「オクタゴン（ダイヤモンドカット）」。
    - 直線壁は 2.4mm（0.6mmノズル×4周で超軽量・約80g台、フィラメントを大幅節約）。
    - アクリルプレート（実寸 76.0mm × 127.0mm × 5.0mm）を上からポンと置くだけの「トップドロップ式」。
      スライド摩擦が文字通りゼロのため、PETG-CFのザラつきによるアクリルの擦り傷が物理的に100%発生しない。
    - 天井庇を全廃し、オーバーハング完全ゼロ（垂れ下がり・糸引きゼロ、サポート材不要）。
    - 内壁は底から上まで完全な長方形（直角 72.4mm × 123.4mm）を維持し、発泡スチロールボード（5.0mm）が真上からストンと敷ける。
    - 四隅の45°ファセット肉厚の中に φ6.0mm × 厚み1.5mm のネオジム磁石を完全に内包・埋め込み。
      外見からは一切磁石の存在が見えず、トップフレームが「パチン！」と吸着。
      開閉時の振動がゼロで、標本の繊細な脚や触覚を痛めず、縦置き展示でもアクリルが確実に保持される。
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
    - case_body: 印刷時間 約1時間10分、フィラメント使用量 約75〜85g（インフィル15%）
    - top_frame: 印刷時間 約12分、フィラメント使用量 約11g

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
WALL_THICKNESS = 2.4        # 外壁直線部の肉厚（0.6mmノズル×4周、超軽量）
TOP_FRAME_THICKNESS = 2.8   # トップフレームの厚み (Z方向、磁石穴上部に1.1mmの頑丈な屋根)
CORNER_CHAMFER_RADIUS = 1.5 # 外郭の各頂点に施す滑らかな微小フィレット半径

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

# 高さ基準 (Z座標)
Z_BOTTOM = 0.0
Z_INNER_FLOOR = BOTTOM_THICKNESS                    # 2.0mm (発泡ボード底)
Z_SHELF = Z_INNER_FLOOR + INNER_DEPTH               # 47.0mm (アクリル受け棚面)
TOTAL_H = Z_SHELF + POCKET_DEPTH                    # 52.0mm (ケース天面)

# 四隅の磁石中心座標 (cx, cy)
# アクリル角 (38.2, 63.7) の外側斜め方向に配置し、十分な樹脂肉厚(1.57mm)を確保
MAG_CX = (POCKET_W / 2) + 3.3                       # 41.5mm
MAG_CY = (POCKET_L / 2) + 3.3                       # 67.0mm

# 直線壁の外側境界
X_WALL = (POCKET_W / 2) + WALL_THICKNESS            # 40.6mm
Y_WALL = (POCKET_L / 2) + WALL_THICKNESS            # 66.1mm


def create_base_sketch() -> Sketch:
    """
    不格好な耳を全廃し、四隅を45°カット（オクタゴン）にした洗練された外郭スケッチを作成します。
    直線部は厚さ2.4mmを維持し、四隅に向かって約13.5°の滑らかなテーパーで広がり、
    角部は45°のダイヤモンドカットでスパッと落とされています。
    """
    # 第1象限（X > 0, Y > 0）のプロファイル頂点 (反時計回り)
    # (40.6, 0.0) -> (40.6, 45.0) -> (46.4, 69.1) -> (43.6, 71.9) -> (20.0, 66.1)
    q1_pts = [
        (X_WALL, 0.0),
        (X_WALL, 45.0),
        (46.4, 69.1),
        (43.6, 71.9),
        (20.0, Y_WALL),
    ]

    pts = []
    # 第1象限
    for x, y in q1_pts:
        pts.append((x, y))
    # 第2象限
    pts.append((0.0, Y_WALL))
    for x, y in reversed(q1_pts):
        pts.append((-x, y))
    # 第3象限
    pts.append((-X_WALL, 0.0))
    for x, y in q1_pts:
        pts.append((-x, -y))
    # 第4象限
    pts.append((0.0, -Y_WALL))
    for x, y in reversed(q1_pts):
        pts.append((x, -y))

    with BuildSketch() as sk:
        poly = Polygon(pts)
        fillet(poly.vertices(), radius=CORNER_CHAMFER_RADIUS)
    return sk.sketch


def build_case_body() -> Part:
    """
    標本ケース本体（case_body）を生成します。
    """
    base_sk = create_base_sketch()

    with BuildPart() as case:
        # 1. オクタゴン外郭ソリッドの押し出し
        extrude(base_sk, amount=TOTAL_H)

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

        # 4. 天面四隅の磁石ポケットを削る（45°コーナー肉厚内に完全に内包）
        corner_locs = [
            (MAG_CX, MAG_CY, TOTAL_H),
            (-MAG_CX, MAG_CY, TOTAL_H),
            (-MAG_CX, -MAG_CY, TOTAL_H),
            (MAG_CX, -MAG_CY, TOTAL_H)
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
    本体と全く同一のオクタゴン外郭を持ちます。
    """
    base_sk = create_base_sketch()

    with BuildPart() as frame:
        # 1. オクタゴン外郭ソリッドの押し出し
        extrude(base_sk, amount=TOP_FRAME_THICKNESS)

        # 2. 中央の窓開口部を削る（標本空間と同じ開口 72.4mm × 123.4mm で完全に上下貫通）
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

        # 4. 指がかり用リセス（長辺中央の両外側にごくわずかな指掛け用ノッチ）
        for side in [-1, 1]:
            with Locations((side * X_WALL, 0, TOP_FRAME_THICKNESS)):
                Box(
                    2.0,
                    24.0,
                    2.0,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    mode=Mode.SUBTRACT
                )

    return frame.part


# ==============================================================================
# 実行とエクスポート
# ==============================================================================
if __name__ == "__main__":
    print("Building Octagon-Corner Magnet Specimen Case...")
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
    print(f"Successfully exported Octagon-Corner STEP to: {output_path}")

    try:
        show_object(case_body, name="case_body")
        show_object(placed_frame, name="top_frame")
    except Exception:
        pass
