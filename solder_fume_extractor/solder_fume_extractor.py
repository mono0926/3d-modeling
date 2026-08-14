from build123d import *
import os
from ocp_vscode import show_object

"""
設計要件:
    - ポータブル扇風機（φ103.5mm x 40.2mm）と活性炭フィルター（130x130x10mm）を組み合わせた卓上ハンダ吸煙器ホルダー。
    - ユーザーの手描き図に基づいた堅牢な一体型ボックス＆ファンネル構造。
    - フィルター部 (130x130x10mm):
        - 上部からスライドインで着脱・交換可能なガイドスロット。
        - 吸引時にフィルターが巻き込まれない強固な背面サポートグリッド（格子壁）。
        - 前面脱落防止用の保持枠（120x120mm 吸気開口）。
    - ファンホルダー部 (φ103.5mm, 厚さ40.2mm):
        - 直径φ105mmの円筒ホルダーでファン全周を確実にホールド。
        - 天面に幅38mmのスリットを設け、持ち手・スイッチ（11.5mm露出）が上に突き出る構造。
        - ファンネルとの境界に段差ストッパーを設け、ファンが前方に落ち込まない。
    - テーパー気室（ファンネル）:
        - 124x124mmのフィルター面からφ105mmのファン吸気口へとスムーズに絞るテーパー構造。
    - 卓上安定性:
        - 幅広でフラットな安定底面ベース。

推奨フィラメント:
    - PETG または PLA

推奨スライサー設定:
    - 壁ループ (Wall Loops): 3〜4回
    - 底面/天面レイヤー: 4〜5層
    - インフィル: 15% (Gyroid または Grid)
    - サポート: なし（底面配置でサポート不要）

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
FRONT_LIP_W = 5.0             # 前面フィルター押さえ枠幅 (開口 122x122mm)
FRONT_WALL_T = 2.5            # 前面枠の厚み
GRID_T = 2.5                  # フィルター背面グリッド厚
CHAMBER_LEN = 16.0            # テーパー気室（ファンネル）長さ
CORNER_RADIUS = 3.0           # 外枠角丸半径

# 外形寸法計算
BOX_W = SLOT_W + (WALL_T * 2)                       # 132 + 6 = 138.0mm
BOX_H = BASE_BOTTOM_T + SLOT_H + WALL_T             # 4 + 130 + 3 = 137.0mm
CENTER_Z = BASE_BOTTOM_T + (SLOT_H / 2.0)           # 4.0 + 65.0 = 69.0mm

# Y軸方向の各ゾーン境界 (原点 Y=0 はフィルター前面外側)
Y_FRONT = 0.0
Y_SLOT_START = FRONT_WALL_T                         # 2.5mm
Y_SLOT_END = Y_SLOT_START + SLOT_T                 # 2.5 + 11.2 = 13.7mm
Y_GRID_END = Y_SLOT_END + GRID_T                   # 13.7 + 2.5 = 16.2mm
Y_CHAMBER_END = Y_GRID_END + CHAMBER_LEN           # 16.2 + 16.0 = 32.2mm
Y_HOLDER_END = Y_CHAMBER_END + HOLDER_DEPTH        # 32.2 + 41.0 = 73.2mm
TOTAL_DEPTH = Y_HOLDER_END

# 出力パスの設定
OUTPUT_FILENAME = "solder_fume_extractor.step"
current_dir = os.path.dirname(__file__)
output_path = os.path.join(current_dir, OUTPUT_FILENAME)


def create_solder_fume_extractor():
    with BuildPart() as model:
        # ----------------------------------------------------
        # 1. 外形メインブロック (一体型ソリッド)
        # ----------------------------------------------------
        # 前面から背面まで安定した直方体ベース
        with BuildSketch(Plane.XY):
            Rectangle(BOX_W, TOTAL_DEPTH)
            fillet(vertices(), radius=CORNER_RADIUS)
        extrude(amount=BOX_H)
        # 中心合わせ: X=0, Y=0〜TOTAL_DEPTH, Z=0〜BOX_H
        # 現在のSketchはXY中心原点なので、位置を調整
        # Boxプリミティブで正確に配置
    
    # 完全に明示的な位置で再構築
    with BuildPart() as model:
        # メインソリッド
        with Locations((0, TOTAL_DEPTH / 2.0, BOX_H / 2.0)):
            Box(BOX_W, TOTAL_DEPTH, BOX_H)

        # 外側の縦4エッジを角丸に
        v_edges = model.edges().filter_by(Axis.Z)
        fillet(v_edges, radius=CORNER_RADIUS)

        # ----------------------------------------------------
        # 2. 前面フィルター吸気開口（吸気窓 122 x 122mm）
        # ----------------------------------------------------
        front_win_w = SLOT_W - (FRONT_LIP_W * 2)  # 122mm
        front_win_h = SLOT_H - (FRONT_LIP_W * 2)  # 120mm
        with Locations((0, -1.0, CENTER_Z)):
            Box(
                front_win_w,
                FRONT_WALL_T + 2.0,
                front_win_h,
                align=(Align.CENTER, Align.MIN, Align.CENTER),
                mode=Mode.SUBTRACT
            )

        # ----------------------------------------------------
        # 3. フィルタースロット（上部から落とし込む溝）
        # ----------------------------------------------------
        with Locations((0, Y_SLOT_START, BASE_BOTTOM_T)):
            Box(
                SLOT_W,
                SLOT_T,
                BOX_H + 5.0,
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # ----------------------------------------------------
        # 4. フィルター背面サポートグリッド（格子壁）
        # Y_SLOT_END から Y_GRID_END (厚さ 2.5mm)
        # ----------------------------------------------------
        grid_area_w = SLOT_W - 6.0   # 126mm
        grid_area_h = SLOT_H - 6.0   # 124mm
        rib_w = 2.5
        grid_pitch = 16.0

        # まずグリッド領域を開口
        with Locations((0, Y_SLOT_END, CENTER_Z)):
            with BuildSketch(Plane(origin=(0, 0, 0), z_dir=(0, 1, 0))):
                Rectangle(grid_area_w, grid_area_h)
            extrude(amount=GRID_T, mode=Mode.SUBTRACT)

        # 縦リブの追加
        num_v = int(grid_area_w / grid_pitch)
        for i in range(-num_v // 2 + 1, num_v // 2 + 1):
            with Locations((i * grid_pitch, Y_SLOT_END + (GRID_T / 2.0), CENTER_Z)):
                Box(rib_w, GRID_T, grid_area_h, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.ADD)

        # 横リブの追加
        num_h = int(grid_area_h / grid_pitch)
        for j in range(-num_h // 2 + 1, num_h // 2 + 1):
            with Locations((0, Y_SLOT_END + (GRID_T / 2.0), CENTER_Z + (j * grid_pitch))):
                Box(grid_area_w, GRID_T, rib_w, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.ADD)

        # ----------------------------------------------------
        # 5. テーパー気室（ファンネル）
        # グリッド開口 (126x124mm) -> ファン吸気口 (φ95mm ストッパー開口)
        # ----------------------------------------------------
        funnel_front_w = grid_area_w
        funnel_front_h = grid_area_h
        funnel_back_dia = HOLDER_INNER_DIA - (FAN_STOPPER_LIP * 2)  # 95.0mm

        with BuildSketch(Plane(origin=(0, Y_GRID_END, CENTER_Z), z_dir=(0, 1, 0))) as sk_f_start:
            Rectangle(funnel_front_w, funnel_front_h)
        with BuildSketch(Plane(origin=(0, Y_CHAMBER_END, CENTER_Z), z_dir=(0, 1, 0))) as sk_f_end:
            Circle(radius=funnel_back_dia / 2.0)
        loft(mode=Mode.SUBTRACT)

        # ----------------------------------------------------
        # 6. ファンホルダー円筒空洞 (完全なφ105mm円筒)
        # Y_CHAMBER_END から 背面 (Y_HOLDER_END) まで
        # ----------------------------------------------------
        with Locations((0, Y_CHAMBER_END, CENTER_Z)):
            with BuildSketch(Plane(origin=(0, 0, 0), z_dir=(0, 1, 0))):
                Circle(radius=HOLDER_INNER_DIA / 2.0)
            extrude(amount=HOLDER_DEPTH + 5.0, mode=Mode.SUBTRACT)

        # ----------------------------------------------------
        # 7. 持ち手・スイッチ用上部スリット (鍵穴状スリット)
        # ファンホルダー部のみ、天面からファン中心まで抜く
        # ----------------------------------------------------
        slit_y_start = Y_CHAMBER_END - 2.0
        slit_y_len = (Y_HOLDER_END - slit_y_start) + 5.0
        slit_height = BOX_H - CENTER_Z + 5.0

        with Locations((0, slit_y_start, CENTER_Z)):
            Box(
                FAN_HANDLE_SLIT_W,
                slit_y_len,
                slit_height,
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # ----------------------------------------------------
        # 8. 仕上げ面取り（フィルター挿入口＆ファン挿入口ガイド）
        # ----------------------------------------------------
        # フィルター挿入口
        filter_inlet_edges = model.edges().filter_by(
            lambda e: e.center().Z > (BOX_H - 1.0) and abs(e.center().X) < (SLOT_W / 2.0) and e.center().Y < Y_GRID_END
        )
        if filter_inlet_edges:
            try:
                chamfer(filter_inlet_edges, length=1.0)
            except Exception:
                pass

        # ファンホルダー背面開口エッジ
        fan_inlet_edges = model.edges().filter_by(
            lambda e: e.center().Y > (Y_HOLDER_END - 1.0) and abs(e.center().X) < (HOLDER_INNER_DIA / 2.0 + 2.0)
        )
        if fan_inlet_edges:
            try:
                chamfer(fan_inlet_edges, length=1.2)
            except Exception:
                pass

    return model.part


if __name__ == "__main__":
    print("Creating solder fume extractor model...")
    result = create_solder_fume_extractor()

    print(f"Exporting to {output_path}...")
    show_object(result)
    export_step(result, output_path)
    print("Done.")
