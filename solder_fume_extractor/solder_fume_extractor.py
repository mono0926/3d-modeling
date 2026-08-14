from build123d import *
import os
from ocp_vscode import show_object

"""
設計要件:
    - ポータブル扇風機（φ103.5mm x 40.2mm）と活性炭フィルター（130x130x10mm）を組み合わせた卓上ハンダ吸煙器ホルダー。
    - 吸引型（手前フィルター -> 中央ファンネル気室 -> 奥ファン -> 後方排気）でファンブレードのヤニ汚れを防止。
    - フィルター部 (130x130x10mm):
        - 上部からスライドインで着脱・交換可能なガイドスロット。
        - 吸引時にフィルターが巻き込まれない背面サポートグリッド（高通気性クロスリブ）。
        - 前面脱落防止用の保持リップ。
    - ファンホルダー部 (φ103.5mm, 厚さ40.2mm):
        - 上部が開放されたU字型クレードルドックにより、ファン本体を上からストンとスライドイン可能。
        - 首元のスイッチ部（11.5mm）を完全に露出させ、装着したまま操作可能なワイドU字スリット。
        - 奥側の抜け止めストッパー（内径92.8mm開口で排気抵抗最小）。
    - 外観・構造デザイン:
        - 前面四角枠から背面円筒へと流麗にシェイプし、大幅な軽量化と印刷時間短縮を実現。
        - 卓上で前後に倒れない安定した低重心ワイドフラットベース。
    - 3Dプリント最適化 (Bambu Lab P2S):
        - 底面配置でサポート材不要。

推奨フィラメント:
    - PETG (耐熱性・耐薬品性・対衝撃性に優れ、ハンダ作業に最適)
    - PLA (一般的な用途で高精度・手軽に印刷可能)

推奨スライサー設定:
    - 壁ループ (Wall Loops): 3〜4回
    - 底面/天面レイヤー (Top/Bottom Shell Layers): 4〜5層
    - インフィル: 15% (Gyroid または Grid)
    - 壁ジェネレーター (Wall generator): Arachne
    - サポート: なし（Support: None）

印刷統計（予想）:
    - solder_fume_extractor: 印刷時間 約2時間20分、フィラメント使用量 約125g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# ==========================================
# パラメーター定義 (mm)
# ==========================================

# フィルター仕様
FILTER_W = 130.0
FILTER_H = 130.0
FILTER_T = 10.0
FILTER_CLEARANCE_W = 2.0      # 左右クリアランス (計 +2.0mm -> 132.0mm)
FILTER_CLEARANCE_T = 1.2      # 厚みクリアランス (+1.2mm -> 11.2mm)

SLOT_W = FILTER_W + FILTER_CLEARANCE_W   # 132.0mm
SLOT_T = FILTER_T + FILTER_CLEARANCE_T   # 11.2mm
SLOT_H = FILTER_H                        # 130.0mm

# ポータブル扇風機仕様
FAN_DIA = 103.5
FAN_THICK = 40.2
FAN_SWITCH_LEN = 11.5         # ファン端面からスイッチまでの長さ
FAN_CLEARANCE_DIA = 1.3       # 直径クリアランス (+1.3mm -> 104.8mm)
FAN_CLEARANCE_THICK = 0.8     # 厚みクリアランス (+0.8mm -> 41.0mm)

HOLDER_INNER_DIA = FAN_DIA + FAN_CLEARANCE_DIA       # 104.8mm
HOLDER_DEPTH = FAN_THICK + FAN_CLEARANCE_THICK       # 41.0mm
FAN_STOPPER_LIP = 6.0         # ファン背面ストッパー幅 (排気開口径 92.8mm)
FAN_NECK_SLIT_W = 42.0        # スイッチ・持ち手露出スリット幅

# 基本構造・肉厚
WALL_T = 2.8                  # 基本外壁厚
BASE_BOTTOM_T = 3.2           # 底面ベース厚
FRONT_LIP_W = 5.5             # 前面フィルター押さえ枠幅 (開口 121x121mm)
FRONT_WALL_T = 2.4            # 前面枠の厚み
GRID_T = 2.2                  # フィルター背面グリッド厚
CHAMBER_LEN = 16.0            # テーパー気室（ファンネル）長さ
CORNER_RADIUS = 3.0           # 外枠角丸半径

# 外形寸法計算
CENTER_Z = BASE_BOTTOM_T + (SLOT_H / 2.0)   # 3.2 + 65.0 = 68.2mm
TOTAL_HEIGHT = BASE_BOTTOM_T + SLOT_H + 2.0  # 135.2mm
FRONT_OUTER_W = SLOT_W + (WALL_T * 2)        # 137.6mm

# Y軸方向の各ゾーン境界 (原点 Y=0 はフィルター前面外側)
Y_FRONT = 0.0
Y_SLOT_START = FRONT_WALL_T                         # 2.4
Y_SLOT_END = Y_SLOT_START + SLOT_T                 # 2.4 + 11.2 = 13.6
Y_GRID_END = Y_SLOT_END + GRID_T                   # 13.6 + 2.2 = 15.8
Y_CHAMBER_END = Y_GRID_END + CHAMBER_LEN           # 15.8 + 16.0 = 31.8
Y_HOLDER_END = Y_CHAMBER_END + HOLDER_DEPTH        # 31.8 + 41.0 = 72.8
Y_BACK = Y_HOLDER_END + WALL_T                     # 72.8 + 2.8 = 75.6
TOTAL_DEPTH = Y_BACK

HOLDER_OUTER_DIA = HOLDER_INNER_DIA + (WALL_T * 2) # 104.8 + 5.6 = 110.4mm

# 出力パスの設定
OUTPUT_FILENAME = "solder_fume_extractor.step"
current_dir = os.path.dirname(__file__)
output_path = os.path.join(current_dir, OUTPUT_FILENAME)


def create_solder_fume_extractor():
    with BuildPart() as model:
        # ----------------------------------------------------
        # 1. 外形メインソリッド
        # 前面四角セクション (Y=0 から Y=Y_GRID_END まで)
        # ----------------------------------------------------
        with BuildSketch(Plane(origin=(0, 0, CENTER_Z), z_dir=(0, 1, 0))):
            Rectangle(FRONT_OUTER_W, TOTAL_HEIGHT)
            fillet(vertices(), radius=CORNER_RADIUS)
        extrude(amount=Y_GRID_END)

        # テーパー部外形ロフト (Y_GRID_END から Y_CHAMBER_END まで)
        with BuildSketch(Plane(origin=(0, Y_GRID_END, CENTER_Z), z_dir=(0, 1, 0))) as s_outer_start:
            Rectangle(FRONT_OUTER_W, TOTAL_HEIGHT)
            fillet(vertices(), radius=CORNER_RADIUS)
        with BuildSketch(Plane(origin=(0, Y_CHAMBER_END, CENTER_Z), z_dir=(0, 1, 0))) as s_outer_end:
            Circle(radius=HOLDER_OUTER_DIA / 2.0)
            with Locations((0, -(CENTER_Z - BASE_BOTTOM_T) / 2.0)):
                Rectangle(HOLDER_OUTER_DIA, CENTER_Z - BASE_BOTTOM_T)
        loft()

        # ファンホルダー部外形 (Y_CHAMBER_END から Y_BACK まで)
        with BuildSketch(Plane(origin=(0, Y_CHAMBER_END, CENTER_Z), z_dir=(0, 1, 0))):
            Circle(radius=HOLDER_OUTER_DIA / 2.0)
            with Locations((0, -(CENTER_Z - BASE_BOTTOM_T) / 2.0)):
                Rectangle(HOLDER_OUTER_DIA, CENTER_Z - BASE_BOTTOM_T)
        extrude(amount=Y_BACK - Y_CHAMBER_END)

        # 安定用ワイドベース（底面の足）
        base_w = FRONT_OUTER_W
        base_d = TOTAL_DEPTH
        with Locations((0, base_d / 2.0, BASE_BOTTOM_T / 2.0)):
            Box(base_w, base_d, BASE_BOTTOM_T, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.ADD)

        # ----------------------------------------------------
        # 2. 前面フィルター吸気開口（吸気窓）
        # ----------------------------------------------------
        front_win_w = SLOT_W - (FRONT_LIP_W * 2)  # 121mm
        front_win_h = SLOT_H - FRONT_LIP_W        # 124.5mm
        with Locations((0, -1.0, CENTER_Z + (FRONT_LIP_W / 2.0))):
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
                TOTAL_HEIGHT + 10.0,
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # ----------------------------------------------------
        # 4. フィルター吸い込み防止グリッド（格子リブ）
        # ----------------------------------------------------
        grid_area_w = SLOT_W - 6.0   # 126mm
        grid_area_h = SLOT_H - 6.0   # 124mm
        rib_w = 2.0

        # グリッド開口のベースくり抜き
        with BuildSketch(Plane(origin=(0, Y_SLOT_END, CENTER_Z), z_dir=(0, 1, 0))):
            Rectangle(grid_area_w, grid_area_h)
        extrude(amount=GRID_T + 0.1, mode=Mode.SUBTRACT)

        # 縦リブ
        num_v = int(grid_area_w / 18.0)
        for i in range(-num_v // 2 + 1, num_v // 2 + 1):
            with Locations((i * 18.0, Y_SLOT_END + (GRID_T / 2.0), CENTER_Z)):
                Box(rib_w, GRID_T, grid_area_h, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.ADD)

        # 横リブ
        num_h = int(grid_area_h / 18.0)
        for j in range(-num_h // 2 + 1, num_h // 2 + 1):
            with Locations((0, Y_SLOT_END + (GRID_T / 2.0), CENTER_Z + (j * 18.0))):
                Box(grid_area_w, GRID_T, rib_w, align=(Align.CENTER, Align.CENTER, Align.CENTER), mode=Mode.ADD)

        # ----------------------------------------------------
        # 5. テーパー気室（ファンネル）内部ロフト
        # ----------------------------------------------------
        with BuildSketch(Plane(origin=(0, Y_GRID_END, CENTER_Z), z_dir=(0, 1, 0))) as sk_inner_start:
            Rectangle(grid_area_w, grid_area_h)
        with BuildSketch(Plane(origin=(0, Y_CHAMBER_END, CENTER_Z), z_dir=(0, 1, 0))) as sk_inner_end:
            Circle(radius=HOLDER_INNER_DIA / 2.0)
        loft(mode=Mode.SUBTRACT)

        # ----------------------------------------------------
        # 6. ファンホルダー円筒空洞
        # ----------------------------------------------------
        with Locations((0, Y_CHAMBER_END, CENTER_Z)):
            with BuildSketch(Plane(origin=(0, 0, 0), z_dir=(0, 1, 0))):
                Circle(radius=HOLDER_INNER_DIA / 2.0)
            extrude(amount=HOLDER_DEPTH, mode=Mode.SUBTRACT)

        # ----------------------------------------------------
        # 7. ファン背面排気口＆抜け止めストッパー
        # ----------------------------------------------------
        stopper_dia = HOLDER_INNER_DIA - (FAN_STOPPER_LIP * 2)  # 92.8mm
        with Locations((0, Y_HOLDER_END, CENTER_Z)):
            with BuildSketch(Plane(origin=(0, 0, 0), z_dir=(0, 1, 0))):
                Circle(radius=stopper_dia / 2.0)
            extrude(amount=WALL_T + 5.0, mode=Mode.SUBTRACT)

        # ----------------------------------------------------
        # 8. ファン上部スライドイン開口（U字クレードルドック）
        # ----------------------------------------------------
        holder_top_cut_w = HOLDER_INNER_DIA
        holder_top_cut_len = (Y_BACK - Y_CHAMBER_END) + 2.0
        with Locations((0, Y_CHAMBER_END - 0.5, CENTER_Z)):
            Box(
                holder_top_cut_w,
                holder_top_cut_len,
                TOTAL_HEIGHT,
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # ----------------------------------------------------
        # 9. 持ち手・スイッチ露出用U字スリット (ファンネル部上部)
        # ----------------------------------------------------
        slit_y_len = (Y_CHAMBER_END - Y_SLOT_END) + 1.0
        with Locations((0, Y_SLOT_END, CENTER_Z - 5.0)):
            Box(
                FAN_NECK_SLIT_W,
                slit_y_len,
                TOTAL_HEIGHT,
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
