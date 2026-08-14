from build123d import *
import os
from ocp_vscode import show_object

"""
設計要件:
    - ポータブル扇風機（φ103.5mm x 40.2mm）と活性炭フィルター（130x130x10mm）を組み合わせた卓上ハンダ吸煙器ホルダー。
    - ユーザーの手描き図に基づいた堅牢な一体型ボックス＆ファンネル構造。
    - フィルター部 (130x130x10mm):
        - 上部からスライドインで着脱・交換可能なガイドスロット。
        - 吸引時にフィルターが巻き込まれない強固な背面サポートグリッド（格子窓アレイ）。
        - 前面脱落防止用の保持枠（122x120mm 吸気開口）。
    - ファンホルダー部 (φ103.5mm, 厚さ40.2mm):
        - 直径φ105.0mmの円筒ホルダーでファン全周を確実にホールド。
        - 天面に幅38.0mmのスリットを設け、持ち手・スイッチ（11.5mm露出）が上に突き出る鍵穴状ドック。
        - ファンネルとの境界に段差ストッパー（φ95.0mm開口）を設け、ファンが前方に落ち込まない。
    - テーパー気室（ファンネル）:
        - 122x120mmのフィルター面からφ95mmのファン吸気口へとスムーズに絞るテーパー構造。
    - 卓上安定性:
        - 幅広でフラットな安定底面ベース (138 x 73.2mm)。
    - 3Dプリント最適化 (Bambu Lab P2S):
        - 底面配置でサポート材完全不要。

推奨フィラメント:
    - PETG または PLA

推奨スライサー設定:
    - 壁ループ (Wall Loops): 3〜4回
    - 底面/天面レイヤー: 4〜5層
    - インフィル: 15% (Gyroid または Grid)
    - サポート: なし（None）
    - 壁ジェネレーター: Arachne

印刷統計（予想）:
    - solder_fume_extractor: 印刷時間 約2時間40分、フィラメント使用量 約145g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# ==========================================
# パラメーター定義 (mm)
# ==========================================

# フィルター寸法
FILTER_W = 130.0
FILTER_H = 130.0
FILTER_T = 10.0
FILTER_CLEARANCE_W = 2.0      # 左右クリアランス (スロット幅 132.0mm)
FILTER_CLEARANCE_T = 1.2      # 厚みクリアランス (スロット厚 11.2mm)

SLOT_W = FILTER_W + FILTER_CLEARANCE_W   # 132.0mm
SLOT_T = FILTER_T + FILTER_CLEARANCE_T   # 11.2mm
SLOT_H = FILTER_H                        # 130.0mm

# ポータブル扇風機寸法
FAN_DIA = 103.5
FAN_THICK = 40.2
FAN_CLEARANCE_DIA = 1.5       # 直径クリアランス (ホルダー内径 105.0mm)
FAN_CLEARANCE_THICK = 0.8     # 厚みクリアランス (ホルダー深さ 41.0mm)

HOLDER_INNER_DIA = FAN_DIA + FAN_CLEARANCE_DIA       # 105.0mm
HOLDER_DEPTH = FAN_THICK + FAN_CLEARANCE_THICK       # 41.0mm
FAN_STOPPER_LIP = 5.0         # ファン前方の段差ストッパー幅 (内径 95.0mm)
FAN_HANDLE_SLIT_W = 38.0      # 持ち手用上部スリット幅

# 基本構造・肉厚
WALL_T = 3.0                  # 基本外壁厚
BASE_BOTTOM_T = 4.0           # 底面ベース厚
FRONT_LIP_W = 5.0             # 前面フィルター押さえ枠幅 (開口 122x120mm)
FRONT_WALL_T = 2.5            # 前面枠の厚み
GRID_T = 2.5                  # フィルター背面グリッド厚
CHAMBER_LEN = 16.0            # テーパー気室（ファンネル）長さ
CORNER_RADIUS = 3.0           # 外枠角丸半径

# 外形寸法計算
BOX_W = SLOT_W + (WALL_T * 2)                       # 138.0mm
BOX_H = BASE_BOTTOM_T + SLOT_H + WALL_T             # 137.0mm
CENTER_Z = BASE_BOTTOM_T + (SLOT_H / 2.0)           # 69.0mm

# Y軸方向の各ゾーン境界 (原点 Y=0 はフィルター前面外側)
Y_FRONT = 0.0
Y_SLOT_START = FRONT_WALL_T                         # 2.5mm
Y_SLOT_END = Y_SLOT_START + SLOT_T                 # 13.7mm
Y_GRID_END = Y_SLOT_END + GRID_T                   # 16.2mm
Y_CHAMBER_END = Y_GRID_END + CHAMBER_LEN           # 32.2mm
Y_BACK = Y_CHAMBER_END + HOLDER_DEPTH              # 73.2mm
TOTAL_DEPTH = Y_BACK

# 出力パスの設定
OUTPUT_FILENAME = "solder_fume_extractor.step"
current_dir = os.path.dirname(__file__)
output_path = os.path.join(current_dir, OUTPUT_FILENAME)


def create_solder_fume_extractor():
    with BuildPart() as model:
        # ----------------------------------------------------
        # 1. 外形メインブロック (X: [-69, +69], Y: [0, 73.2], Z: [0, 137])
        # ----------------------------------------------------
        with Locations((0, TOTAL_DEPTH / 2.0, BOX_H / 2.0)):
            Box(BOX_W, TOTAL_DEPTH, BOX_H)

        # 縦4エッジを角丸に
        v_edges = model.edges().filter_by(Axis.Z).filter_by(lambda e: abs(e.center().X) > (BOX_W / 2.0 - 1.0))
        if v_edges:
            fillet(v_edges, radius=CORNER_RADIUS)

        # ----------------------------------------------------
        # 2. 前面フィルター吸気開口（吸気窓 122 x 120mm）
        # 前面 (Y=0) から +Y 方向へ FRONT_WALL_T 分だけくり抜く
        # ----------------------------------------------------
        front_win_w = SLOT_W - (FRONT_LIP_W * 2)  # 122mm
        front_win_h = SLOT_H - (FRONT_LIP_W * 2)  # 120mm
        with Locations((0, -0.1, CENTER_Z)):
            Box(
                front_win_w,
                FRONT_WALL_T + 0.2,
                front_win_h,
                align=(Align.CENTER, Align.MIN, Align.CENTER),
                mode=Mode.SUBTRACT
            )

        # ----------------------------------------------------
        # 3. フィルタースロット（上部から落とし込む溝）
        # 天面 (Z=BOX_H) から底面 (Z=BASE_BOTTOM_T) までくり抜く
        # ----------------------------------------------------
        with Locations((0, Y_SLOT_START, BASE_BOTTOM_T)):
            Box(
                SLOT_W,
                SLOT_T,
                BOX_H - BASE_BOTTOM_T + 1.0,
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # ----------------------------------------------------
        # 4. フィルター背面サポートグリッド（格子窓アレイ）
        # Y_SLOT_END (13.7mm) から Y_GRID_END (16.2mm) の壁に格子穴を開ける
        # ----------------------------------------------------
        hole_size = 13.5
        bar_w = 2.5
        pitch = hole_size + bar_w  # 16.0mm
        cols = 7
        rows = 7
        for r in range(-(rows // 2), rows // 2 + 1):
            for c in range(-(cols // 2), cols // 2 + 1):
                with Locations((c * pitch, Y_SLOT_END - 0.1, CENTER_Z + (r * pitch))):
                    Box(
                        hole_size,
                        GRID_T + 0.2,
                        hole_size,
                        align=(Align.CENTER, Align.MIN, Align.CENTER),
                        mode=Mode.SUBTRACT
                    )

        # ----------------------------------------------------
        # 5. テーパー気室（ファンネル）
        # Y_GRID_END (16.2mm) -> Y_CHAMBER_END (32.2mm)
        # 四角 (122x120mm) -> 円 (φ95.0mm)
        # ----------------------------------------------------
        p_f_start = Plane(origin=(0, Y_GRID_END, CENTER_Z), x_dir=(1, 0, 0), z_dir=(0, 0, 1))
        p_f_end = Plane(origin=(0, Y_CHAMBER_END, CENTER_Z), x_dir=(1, 0, 0), z_dir=(0, 0, 1))
        with BuildSketch(p_f_start) as sk1:
            Rectangle(122.0, 120.0)
        with BuildSketch(p_f_end) as sk2:
            Circle(radius=95.0 / 2.0)
        loft(mode=Mode.SUBTRACT)

        # ----------------------------------------------------
        # 6. ファンホルダー円筒空洞 (完全なφ105.0mm円筒)
        # Y_CHAMBER_END (32.2mm) から 背面 (Y_BACK = 73.2mm) へ貫通
        # ----------------------------------------------------
        with Locations(Location((0, Y_CHAMBER_END - 0.1, CENTER_Z), (90, 0, 0))):
            Cylinder(
                radius=HOLDER_INNER_DIA / 2.0,
                height=HOLDER_DEPTH + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # ----------------------------------------------------
        # 7. 持ち手・スイッチ用上部スリット (鍵穴型)
        # ファンホルダー部 (Y_CHAMBER_END〜Y_BACK) の真上を天面までくり抜く
        # ----------------------------------------------------
        with Locations((0, Y_CHAMBER_END - 0.1, CENTER_Z)):
            Box(
                FAN_HANDLE_SLIT_W,
                HOLDER_DEPTH + 1.0,
                BOX_H - CENTER_Z + 1.0,
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT
            )

    return model.part


if __name__ == "__main__":
    print("Creating solder fume extractor model...")
    result = create_solder_fume_extractor()

    print(f"Exporting to {output_path}...")
    show_object(result)
    export_step(result, output_path)
    print("Done.")
