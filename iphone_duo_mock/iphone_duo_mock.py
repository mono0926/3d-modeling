"""
設計要件:
    - iPhone Duo の折りたたみモックモデル（実寸大・可動式）。
    - 公式スペック寸法に忠実な設計:
        - 開いた時 (Unfolded): 幅 164.6mm × 高さ 117.8mm × 厚さ 5.2mm (画面: 7.6インチ)
        - 閉じた時 (Folded): 幅 84.1mm × 高さ 117.8mm × 厚さ 11.3mm (画面: 5.4インチ)
    - 折りたたみ機構（ヒンジ）:
        - 3Dプリンター用 1.75mm PLAフィラメントの切れ端をピン軸として差し込むインターロッキングヒンジ。
        - ピン穴径 2.0mm（抵抗なく滑らかに回転し抜けにくい適正公差）。
        - 7セグメント噛み合わせナックル（軸方向クリアランス 0.35mm、回転逃げ 0.35mm）。
        - 閉じた時に画面同士が平行に合わさり、外寸がぴったり 84.1mm × 11.3mm になる幾何学配置。
    - 3Dプリント適性（Bambu Lab P2S 等を想定）:
        - サポート材完全不要（Support-Free）。
        - 背面（フラット面）を下にしてビルドプレートに配置することで、反りを抑え最高精度の表面とヒンジ強度を実現。
        - メインディスプレイ領域（内側）およびカバーディスプレイ領域（外側）に深さ 0.45mm / 0.20mm のデボスを配置。
          Bambu Studio等でマルチカラー塗り分け（画面を黒にする等）がワンクリックで可能。
    - モデルごとに専用ディレクトリで管理し、STEPファイルを出力する。

推奨フィラメント:
    - PLA（PLA Basic, PLA Matte 等。寸法精度が高くヒンジの噛み合わせが最も滑らか）。
    - 軸ピンにはお手持ちの 1.75mm PLA フィラメントの切れ端（約120mm長）を使用。
    - PETG でも造形可能（公差がややタイトになる場合はピンを少しヤスリがけするか押し込み）。

推奨スライサー設定:
    - 積層ピッチ (Layer Height): 0.16mm 〜 0.20mm (0.16mm Optimal 推奨)
    - 外壁数 (Wall Loops): 3 〜 4（ヒンジナックルの強度を最大化するため）
    - インフィル (Infill): 15% 〜 20%（ジャイロイド推奨）
    - サポート (Support): なし (None / 完全に不要)
    - ブリム (Brim): 自動 または 必要に応じて内側ブリム
    - 印刷向き: 背面（フラット面 Z=0）をベッドに接地させて平置き配置

印刷統計（予想）:
    - iphone_duo_mock.step (両パーツ合計): 印刷時間 約1時間30分〜2時間、フィラメント使用量 約110〜125g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import os
from build123d import *

# ============================================================
# パラメーター定義 (単位: mm)
# ============================================================

# 公式スペック寸法
OVERALL_WIDTH_OPEN = 164.60         # 開いた時の全幅
OVERALL_HEIGHT = 117.80             # 全高
BODY_THICKNESS = 5.20               # 開いた時の画面部厚さ
CLOSED_THICKNESS = 11.30            # 閉じた時の総厚さ
CLOSED_WIDTH = 84.10                # 閉じた時の全幅

# 半身の幾何学
HALF_WIDTH = OVERALL_WIDTH_OPEN / 2.0         # 82.30 mm (片側ボディ幅)
BEZEL_HEIGHT = CLOSED_THICKNESS / 2.0         # 5.65 mm (外周ベゼル高さ)
MAIN_SCREEN_DEBOSS = BEZEL_HEIGHT - BODY_THICKNESS  # 0.45 mm (メイン画面の凹み深さ)

# コーナーR (外観意匠)
CORNER_RADIUS_OUTER = 11.00         # iPhoneらしい外側コーナーR
CORNER_RADIUS_INNER = 1.00          # ヒンジ側コーナーR

# ディスプレイ領域寸法
MAIN_BEZEL_OUTER = 3.80             # 内側メイン画面の外周ベゼル幅
MAIN_BEZEL_HINGE = 3.00             # 内側メイン画面のヒンジ側ベゼル幅
MAIN_SCREEN_CORNER_R = 8.00         # メイン画面コーナーR

COVER_SCREEN_WIDTH = 73.00          # 外側カバー画面幅 (約5.4インチ)
COVER_SCREEN_HEIGHT = 108.80        # 外側カバー画面高さ
COVER_SCREEN_CORNER_R = 9.00        # カバー画面コーナーR
COVER_SCREEN_DEBOSS = 0.20          # カバー画面の凹み深さ (ベッド面用控えめデボス)

# ヒンジ幾何学 (1.75mmフィラメントピン軸)
PIN_DIAMETER = 2.00                 # 1.75mmフィラメント用ピン穴径
PIN_RADIUS = PIN_DIAMETER / 2.0     # 1.00 mm
HINGE_RADIUS = CLOSED_WIDTH - HALF_WIDTH  # 1.80 mm (84.1 - 82.3 = 1.8mm)
PIVOT_Z = BEZEL_HEIGHT              # 5.65 mm (内面ベゼル上面とツライチの回転軸)

NUM_SEGMENTS = 7                    # ナックル分割数
SEGMENT_PITCH = OVERALL_HEIGHT / NUM_SEGMENTS  # 約 16.83 mm
GAP_Y = 0.35                        # 軸方向クリアランス
GAP_RADIAL = 0.35                   # 半径方向クリアランス
CUTOUT_RADIUS = HINGE_RADIUS + GAP_RADIAL  # 2.15 mm (相手ナックルの受容半径)


# ============================================================
# モデリング関数
# ============================================================

def create_half_body(is_left: bool) -> Solid:
    """
    iPhone Duo の片側（左半身または右半身）を構築する。

    座標系:
        原点 (0, 0, 0): ヒンジ中心線の底面 (Z=0)
        +X: 右半身側, -X: 左半身側
        +Y / -Y: 高さ方向 (中央が Y=0)
        +Z: 厚さ方向 (Z=0 が背面フラット面、Z=5.65 が画面ベゼル上面)
    """
    sign = -1.0 if is_left else 1.0

    with BuildPart() as body:
        # ----------------------------------------------------------
        # 1. ベースボディ (Z in [0, BEZEL_HEIGHT])
        # ----------------------------------------------------------
        with BuildSketch() as base_sk:
            with BuildLine():
                if is_left:
                    p_lb = (-HALF_WIDTH, -OVERALL_HEIGHT / 2.0)
                    p_rb = (0.0, -OVERALL_HEIGHT / 2.0)
                    p_rt = (0.0, OVERALL_HEIGHT / 2.0)
                    p_lt = (-HALF_WIDTH, OVERALL_HEIGHT / 2.0)
                else:
                    p_lb = (0.0, -OVERALL_HEIGHT / 2.0)
                    p_rb = (HALF_WIDTH, -OVERALL_HEIGHT / 2.0)
                    p_rt = (HALF_WIDTH, OVERALL_HEIGHT / 2.0)
                    p_lt = (0.0, OVERALL_HEIGHT / 2.0)
                Polyline([p_lb, p_rb, p_rt, p_lt, p_lb])
            make_face()

            # 角丸フィレット (外側2頂点に iPhone R, 内側2頂点に小R)
            if is_left:
                v_outer = base_sk.vertices().sort_by(Axis.X)[:2]
                v_inner = base_sk.vertices().sort_by(Axis.X)[2:]
            else:
                v_inner = base_sk.vertices().sort_by(Axis.X)[:2]
                v_outer = base_sk.vertices().sort_by(Axis.X)[2:]
            fillet(v_outer, radius=CORNER_RADIUS_OUTER)
            fillet(v_inner, radius=CORNER_RADIUS_INNER)

        extrude(amount=BEZEL_HEIGHT)

        # ----------------------------------------------------------
        # 2. 内側メインディスプレイ領域のデボス (上面 Z = BEZEL_HEIGHT)
        # ----------------------------------------------------------
        with BuildSketch(Plane.XY.offset(BEZEL_HEIGHT)) as main_screen_sk:
            scr_w = HALF_WIDTH - MAIN_BEZEL_OUTER - MAIN_BEZEL_HINGE
            scr_h = OVERALL_HEIGHT - 2 * MAIN_BEZEL_OUTER
            if is_left:
                scr_cx = -MAIN_BEZEL_HINGE - scr_w / 2.0
            else:
                scr_cx = MAIN_BEZEL_HINGE + scr_w / 2.0
            with Locations([(scr_cx, 0)]):
                RectangleRounded(scr_w, scr_h, MAIN_SCREEN_CORNER_R)
        extrude(amount=-MAIN_SCREEN_DEBOSS, mode=Mode.SUBTRACT)

        # ----------------------------------------------------------
        # 3. 外側カバーディスプレイ領域のデボス (左半身の背面 Z = 0)
        # ----------------------------------------------------------
        if is_left:
            with BuildSketch(Plane.XY) as cover_screen_sk:
                # 閉じた時のカバーディスプレイ中央配置
                cover_cx = -HALF_WIDTH / 2.0
                with Locations([(cover_cx, 0)]):
                    RectangleRounded(COVER_SCREEN_WIDTH, COVER_SCREEN_HEIGHT, COVER_SCREEN_CORNER_R)
            extrude(amount=COVER_SCREEN_DEBOSS, mode=Mode.SUBTRACT)

        # ----------------------------------------------------------
        # 4. ヒンジナックルの追加 (自分がナックルを持つセグメント)
        #    左半身: 偶数セグメント (0, 2, 4, 6)
        #    右半身: 奇数セグメント (1, 3, 5)
        # ----------------------------------------------------------
        my_segments = [i for i in range(NUM_SEGMENTS) if (i % 2 == 0) == is_left]
        other_segments = [i for i in range(NUM_SEGMENTS) if (i % 2 == 0) != is_left]

        y_start = -OVERALL_HEIGHT / 2.0

        for i in my_segments:
            y_seg_min = y_start + i * SEGMENT_PITCH
            y_seg_max = y_start + (i + 1) * SEGMENT_PITCH

            # 端部以外の境界にクリアランスを適用
            if i > 0:
                y_seg_min += GAP_Y / 2.0
            if i < NUM_SEGMENTS - 1:
                y_seg_max -= GAP_Y / 2.0

            seg_len = y_seg_max - y_seg_min
            seg_center_y = (y_seg_min + y_seg_max) / 2.0

            # ナックル円筒
            with Locations([(0, seg_center_y, PIVOT_Z)]):
                Cylinder(radius=HINGE_RADIUS, height=seg_len, rotation=(90, 0, 0))

            # ナックル下部のブリッジ直方体 (底面 Z=0 まで一体化して強度を確保)
            bridge_x = -HINGE_RADIUS / 2.0 if is_left else HINGE_RADIUS / 2.0
            with Locations([(bridge_x, seg_center_y, BEZEL_HEIGHT / 2.0)]):
                Box(HINGE_RADIUS, seg_len, BEZEL_HEIGHT)

        # ----------------------------------------------------------
        # 5. 相手ナックルの逃げスロット (切り欠きポケット)
        # ----------------------------------------------------------
        for i in other_segments:
            y_seg_min = y_start + i * SEGMENT_PITCH - (GAP_Y / 2.0 if i > 0 else 0.0)
            y_seg_max = y_start + (i + 1) * SEGMENT_PITCH + (GAP_Y / 2.0 if i < NUM_SEGMENTS - 1 else 0.0)

            seg_len = y_seg_max - y_seg_min
            seg_center_y = (y_seg_min + y_seg_max) / 2.0

            # 相手ナックル円筒の逃げ
            with Locations([(0, seg_center_y, PIVOT_Z)]):
                Cylinder(radius=CUTOUT_RADIUS, height=seg_len, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

            # 相手ナックルの回転動作用クリアランススロット
            slot_x = -CUTOUT_RADIUS / 2.0 if is_left else CUTOUT_RADIUS / 2.0
            with Locations([(slot_x, seg_center_y, BEZEL_HEIGHT / 2.0)]):
                Box(CUTOUT_RADIUS, seg_len, BEZEL_HEIGHT + CUTOUT_RADIUS, mode=Mode.SUBTRACT)

        # ----------------------------------------------------------
        # 6. ピン軸貫通穴 (1.75mmフィラメント用 直径 2.0mm)
        # ----------------------------------------------------------
        with Locations([(0, 0, PIVOT_Z)]):
            Cylinder(radius=PIN_RADIUS, height=OVERALL_HEIGHT + 4.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

    part = body.part
    part.label = "iphone_duo_left" if is_left else "iphone_duo_right"
    return part


def gen_step():
    """
    iPhone Duo の左半身・右半身を生成し、アセンブリ（Compound）として返す。
    CADスキルおよび Bambu Studio 連携用エントリーポイント。
    """
    left_part = create_half_body(is_left=True)
    right_part = create_half_body(is_left=False)

    assembly = Compound([left_part, right_part], label="iphone_duo_mock")
    return assembly, left_part, right_part


# ============================================================
# スクリプト直接実行時: STEPファイル出力とプレビュー
# ============================================================

if __name__ == "__main__":
    from ocp_vscode import show_object

    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("iPhone Duo モックモデルを生成中...")
    assembly, left_part, right_part = gen_step()

    # STEPファイル出力
    main_step_path = os.path.join(script_dir, "iphone_duo_mock.step")
    left_step_path = os.path.join(script_dir, "iphone_duo_left.step")
    right_step_path = os.path.join(script_dir, "iphone_duo_right.step")

    export_step(assembly, main_step_path)
    export_step(left_part, left_step_path)
    export_step(right_part, right_step_path)

    print(f"STEP (Assembly) 出力完了: {main_step_path}")
    print(f"STEP (Left Half) 出力完了: {left_step_path}")
    print(f"STEP (Right Half) 出力完了: {right_step_path}")

    # 寸法と干渉の最終検証
    overlap = left_part.intersect(right_part)
    assert overlap is None, "エラー: 開いた状態で左右パーツの干渉が検出されました。"

    # 180度折りたたみシミュレーション
    pivot_axis = Axis((0, 0, PIVOT_Z), (0, 1, 0))
    left_folded = left_part.rotate(pivot_axis, 180)
    overlap_folded = left_folded.intersect(right_part)
    assert overlap_folded is None, "エラー: 折りたたみ時に左右パーツの干渉が検出されました。"

    folded_comp = Compound([left_folded, right_part])
    f_bbox = folded_comp.bounding_box()
    print(f"折りたたみ時寸法: 幅={f_bbox.size.X:.2f}mm (目標 84.1mm), 高さ={f_bbox.size.Y:.2f}mm (目標 117.8mm), 厚さ={f_bbox.size.Z:.2f}mm (目標 11.3mm)")

    o_bbox = assembly.bounding_box()
    print(f"展開時寸法: 幅={o_bbox.size.X:.2f}mm (目標 164.6mm), 高さ={o_bbox.size.Y:.2f}mm (目標 117.8mm)")

    # プレビュー表示
    show_object(assembly, name="iphone_duo_mock")
