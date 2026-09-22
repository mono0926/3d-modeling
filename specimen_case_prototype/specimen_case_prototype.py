import math
import os
from build123d import *
from ocp_vscode import show_object

"""
設計要件:
    - 昆虫標本（国産カブトムシ等）用の最高級・完全フラット直方体（ソリッド・モノリス）標本ケース。
    - 一切の突起・耳・段差を完全に排除した「端正で美しい完全フラット直方体（四隅R3.0mmフィレット）」。
    - 本体と蓋（トップフレーム）の外形寸法（幅 91.2mm × 長さ 142.2mm）が完全に一致（ツライチ）。
      蓋を重ねた際、一本の美しいスリットのみが見える、Apple製品や高級ジュエリーケースのような佇まい。
    - 0.6mmノズル ＆ PETG-CF の高剛性を活かし、強度を完璧に保ちながらフィラメント使用量を極限まで削減：
      1. 外形寸法を磁石配置に合わせてミリ単位で最小化（91.2mm × 142.2mm）。
      2. 底面ベース厚みを 1.44mm（0.24mm × 6層 = ボトム3層＋トップ3層）に最適化（剛性を保ちつつ軽量化）。
      3. 蓋（トップフレーム）の厚みを 2.40mm（0.24mm × 10層）にスリム化（蓋単体でわずか約11g）。
      4. アクリル受け棚幅を 1.8mm に最適化し、開口部を広げて樹脂量を削減。
    - すべての Z 寸法を 0.24mm レイヤー高さの完全整数倍に整合（スライサーの丸め誤差ゼロ）。
    - 磁石穴公差を 0.6mm ノズル用に最適化（穴径 6.4mm × 深さ 1.68mm〜1.92mm）：
      0.6mmノズルの樹脂収縮を完全に相殺し、φ6.0mm × 1.5mm ネオジム磁石が接着剤とともに確実にツライチ以下に沈み込みます。
    - アクリルプレート（実寸 76.0mm × 127.0mm × 5.0mm）を上からポンと置くだけの「トップドロップ式」。
      スライド摩擦が文字通りゼロのため、PETG-CFのザラつきによるアクリルの擦り傷が物理的に100%発生しない。
    - 天井庇を全廃し、オーバーハング完全ゼロ（垂れ下がり・糸引きゼロ、サポート材不要）。
    - 内壁は底から上まで完全な長方形（直角 72.8mm × 123.8mm）を維持し、発泡スチロールボード（5.0mm）が真上からストンと敷ける。

推奨フィラメント & ノズル:
    - フィラメント: Bambu PETG-CF 黒 (Black)
    - ノズル: 0.6mm タングステンノズル (または硬化鋼ノズル)

推奨スライサー設定 (Bambu Studio - 軽量・高強度・高速最適化):
    - ノズル径: 0.6mm
    - レイヤー高さ: 0.24mm Standard (全高さが0.24mmの完全整数倍)
    - 壁ループ (Wall Loops): 2 (外壁1.24mm＋内壁1.24mmでPETG-CFとして十分すぎる高剛性・軽量化の要)
    - トップシェルレイヤー: 3層 (0.72mm)
    - ボトムシェルレイヤー: 3層 (0.72mm)
    - 疎らインフィル密度: 10%
    - 疎らインフィルパターン: Cross Hatch (または Gyroid) ※Cross Hatchは高速かつ省フィラメント
    - サポート: なし (None / オーバーハング完全ゼロ設計)
    - 円弧フィッティング (Arc fitting): 有効 (Enable)

印刷統計（予想 - 0.6mmノズル / 0.24mmレイヤー / 壁ループ2 / インフィル10% Cross Hatch）:
    - case_body: フィラメント使用量 約105g〜110g
    - top_frame: フィラメント使用量 約11g
    - 合計: 約116g〜120g（耳付きモデルの138gより約20g軽量化！）
    - 印刷時間: 約1時間50分〜2時間10分（直方体で加減速が激減し、3時間から大幅短縮！）

磁石の接着について（重要）:
    - φ6.0mm × 厚み1.5mm のネオジム磁石を計8個（本体4個 ＋ トップフレーム4個）使用します。
    - 本体とトップフレームが互いに引き合うよう、極性（N極/S極）の向きを合わせて瞬間接着剤等で固定してください。

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# ==============================================================================
# パラメーター設定 (単位: mm)
# ==============================================================================

# --- レイヤー高さ基準 ---
LAYER_HEIGHT = 0.24         # 0.6mmノズルの標準レイヤー高さ

# --- アクリルプレート実寸 ---
ACRYLIC_WIDTH = 76.0        # 短辺 (X方向) ※20cm時は 200.0
ACRYLIC_LENGTH = 127.0      # 長辺 (Y方向) ※20cm時は 200.0
ACRYLIC_THICKNESS = 5.0     # 厚み (Z方向、実測値)

# --- 標本空間 & 発泡スチロールボード ---
# 0.24mm × 188層 = 45.12mm (発泡ボード5.0mm + 標本深さ約40.1mm)
INNER_DEPTH = 188 * LAYER_HEIGHT
SHELF_WIDTH = 1.8           # アクリル板を受ける外周段差の幅 (四辺均等1.8mmでアクリルを保持)

# --- ケース基本構造 ---
# 0.24mm × 6層 = 1.44mm (ボトム3層+トップ3層、0.6mm PETG-CFとして十分な高剛性底板)
BOTTOM_THICKNESS = 6 * LAYER_HEIGHT

# 0.24mm × 10層 = 2.40mm (額縁幅9.2mmにより2.40mmでたわみゼロの超軽量蓋)
TOP_FRAME_THICKNESS = 10 * LAYER_HEIGHT
CORNER_RADIUS = 3.0         # 四隅の外郭フィレット半径

# --- ネオジム磁石 (実寸 φ6.0mm × 1.5mm) ---
MAGNET_DIAMETER = 6.0       # 磁石直径
MAGNET_THICKNESS = 1.5      # 磁石厚み
MAGNET_HOLE_D = 6.4         # 磁石穴直径 (0.6mmノズル収縮マージン+接着剤逃げしろ)
# 本体側: 0.24mm × 8層 = 1.92mm
MAGNET_HOLE_DEPTH_BODY = 8 * LAYER_HEIGHT
# 蓋側: 0.24mm × 7層 = 1.68mm (天面に0.72mm=3層のソリッド肉厚を確保)
MAGNET_HOLE_DEPTH_FRAME = 7 * LAYER_HEIGHT

# --- 公差（クリアランス） ---
POCKET_CLEARANCE_XY = 0.4   # アクリル落とし込み用遊び (片側 0.2mm)

# ==============================================================================
# 計算される派生寸法
# ==============================================================================

# アクリルポケット寸法（本体天面の掘り込み）
POCKET_W = ACRYLIC_WIDTH + POCKET_CLEARANCE_XY      # 76.4mm
POCKET_L = ACRYLIC_LENGTH + POCKET_CLEARANCE_XY    # 127.4mm
# 0.24mm × 21層 = 5.04mm (アクリル5.0mmに対して+0.04mmで完璧なツライチ)
POCKET_DEPTH = 21 * LAYER_HEIGHT

# 標本・ボード空間の内寸（開口部）
INNER_W = POCKET_W - 2 * SHELF_WIDTH                # 72.8mm
INNER_L = POCKET_L - 2 * SHELF_WIDTH                # 123.8mm

# 磁石中心座標 (cx, cy)
# アクリル角 (38.2, 63.7) との間に1.0mmの隔壁を確保
diag_dist = 1.0 + (MAGNET_HOLE_D / 2)               # 4.2mm
diag_offset = diag_dist / math.sqrt(2)              # 約 2.97mm
MAG_CX = (POCKET_W / 2) + diag_offset               # 41.17mm
MAG_CY = (POCKET_L / 2) + diag_offset               # 66.67mm

# 外形寸法（ミリ単位で最小化した完全フラット直方体）
# 磁石外側に1.23mm以上の外壁肉厚を確保
TOTAL_W = 91.2                                      # X: ±45.6mm
TOTAL_L = 142.2                                     # Y: ±71.1mm

# ケース本体の総高さ (0.24mm × 215層 = 51.60mm)
TOTAL_H = BOTTOM_THICKNESS + INNER_DEPTH + POCKET_DEPTH

# 各高さ基準 (Z座標)
Z_BOTTOM = 0.0
Z_INNER_FLOOR = BOTTOM_THICKNESS                    # 1.44mm (発泡ボード底)
Z_SHELF = Z_INNER_FLOOR + INNER_DEPTH               # 46.56mm (アクリル受け棚面)
Z_TOP = TOTAL_H                                     # 51.60mm (ケース天面)


def create_base_sketch() -> Sketch:
    """
    一切の突起・耳・くびれのない、美しく角丸（R3.0mm）を施した完全フラット長方形の外郭プロファイルを作成します。
    """
    with BuildSketch() as sk:
        r = Rectangle(TOTAL_W, TOTAL_L)
        fillet(r.vertices(), radius=CORNER_RADIUS)
    return sk.sketch


def build_case_body() -> Part:
    """
    標本ケース本体（case_body）を生成します。
    完全フラット直方体・底厚1.44mm軽量設計。
    """
    base_sk = create_base_sketch()

    with BuildPart() as case:
        # 1. 外郭ソリッドの押し出し（完全フラット直方体）
        extrude(base_sk, amount=TOTAL_H)

        # 2. 標本＆発泡ボードの内部空間を削る（Z=1.44 から上まで完全な長方形 72.8mm × 123.8mm）
        with Locations((0, 0, Z_INNER_FLOOR)):
            Box(
                INNER_W,
                INNER_L,
                TOTAL_H - Z_INNER_FLOOR + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 3. アクリル落とし込みポケットを削る（Z=46.56 から天面まで）
        with Locations((0, 0, Z_SHELF)):
            Box(
                POCKET_W,
                POCKET_L,
                POCKET_DEPTH + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 4. 天面四隅の磁石ポケットを削る（外郭肉厚内に完全に内包、深さ 1.92mm = 8層）
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
                    height=MAGNET_HOLE_DEPTH_BODY,
                    align=(Align.CENTER, Align.CENTER, Align.MAX),
                    mode=Mode.SUBTRACT
                )

    return case.part


def build_top_frame() -> Part:
    """
    蓋（top_frame）を生成します。
    本体と全く同一の完全フラット外郭（幅91.2mm × 長さ142.2mm、角丸R3mm）を持ちます。
    厚み 2.40mm（10層）、天面肉厚 0.72mm（3層の完全平滑シェル）。
    """
    base_sk = create_base_sketch()

    with BuildPart() as frame:
        # 1. 外郭ソリッドの押し出し（Z=0 から Z=2.40mm）
        extrude(base_sk, amount=TOP_FRAME_THICKNESS)

        # 2. 中央の窓開口部を【完全に上下貫通】して削る（Z=-1.0 から完全に削り落とす）
        with Locations((0, 0, -1.0)):
            Box(
                INNER_W,
                INNER_L,
                TOP_FRAME_THICKNESS + 2.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 3. 裏面（下面 Z=0）四隅の磁石ポケットを削る（深さ 1.68mm = 7層）
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
                    height=MAGNET_HOLE_DEPTH_FRAME,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT
                )

    return frame.part


# ==============================================================================
# 実行とエクスポート
# ==============================================================================
if __name__ == "__main__":
    print("Building Optimized Solid Monolith Rectangular Specimen Case...")
    case_body = build_case_body()
    top_frame = build_top_frame()

    print(f"Case Body Bounding Box: {case_body.bounding_box()}")
    print(f"Top Frame Bounding Box: {top_frame.bounding_box()}")
    print(f"Case Body Solid Volume: {case_body.volume / 1000.0:.2f} cm3")
    print(f"Top Frame Solid Volume: {top_frame.volume / 1000.0:.2f} cm3")

    # アセンブリ配置: ワンプレート印刷
    # 本体の右側にトップフレームを並べて配置（Z=0接地）
    placed_frame = top_frame.moved(Location((TOTAL_W + 16.0, 0, 0)))
    assembly = Compound(children=[case_body, placed_frame])

    output_dir = os.path.dirname(__file__)
    output_path = os.path.join(output_dir, "specimen_case_prototype.step")

    export_step(assembly, output_path)
    print(f"Successfully exported Optimized Solid Monolith STEP to: {output_path}")

    try:
        show_object(case_body, name="case_body")
        show_object(placed_frame, name="top_frame")
    except Exception:
        pass
