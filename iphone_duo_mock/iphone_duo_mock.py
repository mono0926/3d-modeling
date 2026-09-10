"""
設計要件:
    - iPhone Duo の折りたたみモックモデル（実寸大・可動式・マルチカラー対応）。
    - 画面および外観を完全フラット（ツライチ）にしつつ、Bambu Studio で別フィラメントを指定できる
      厚さ 1層分（0.20mm）の別パーツ（隙間ゼロ・完全密着ソリッド）として構成。
    - 公式スペック寸法に忠実な設計:
        - 開いた時 (Unfolded): 幅 164.6mm × 高さ 117.8mm × 厚さ 5.2mm (画面: 7.6インチ)
        - 閉じた時 (Folded): 幅 84.1mm × 高さ 117.8mm × 厚さ 10.4mm (画面: 5.4インチ)
    - マルチカラー (AMS) 対応構造:
        - 表面に物理的な凹凸（デボス）がなく、触感・外観ともに完全フラット。
        - 以下の5つの独立ソリッドで構成され、Bambu Studio のオブジェクトリストから各パーツに
          フィラメント番号（例: ボディ=白/チタン、スクリーン=黒）を指定するだけで美しい2色造形が可能:
            1. `left_body`: 左半身本体 (厚さ 5.2mm)
            2. `left_screen`: 左内側メイン画面 (厚さ 0.20mm、上面ツライチ密着)
            3. `cover_screen`: 外側カバー画面 (厚さ 0.20mm、底面ツライチ密着)
            4. `right_body`: 右半身本体 (厚さ 5.2mm)
            5. `right_screen`: 右内側メイン画面 (厚さ 0.20mm、上面ツライチ密着)
    - 折りたたみ機構（ヒンジ）:
        - 3Dプリンター用 1.75mm PLAフィラメントの切れ端をピン軸として差し込むインターロッキングヒンジ。
        - ピン穴径 2.0mm（抵抗なく滑らかに回転し抜けにくい適正公差）。
        - 7セグメント噛み合わせナックル（軸方向クリアランス 0.35mm、回転逃げ 0.35mm）。
        - 閉じた時に画面同士が平行・ぴったり密着して合わさり、幅 84.1mm になる幾何学配置。
    - 3Dプリント適性（Bambu Lab P2S 等を想定）:
        - サポート材完全不要（Support-Free）。
        - 背面（フラット面 Z=0）をベッドに接地させて平置き配置。
    - モデルごとに専用ディレクトリで管理し、STEPファイルを出力する。

推奨フィラメント:
    - ボディ: PLA Basic / PLA Matte（ホワイト、チタニウムグレー等）
    - スクリーン: PLA Basic（ブラック）
    - ヒンジ軸ピン: お手持ちの 1.75mm PLA フィラメントの切れ端（約120mm長）

推奨スライサー設定:
    - 積層ピッチ (Layer Height): 0.20mm (Standard) または 0.16mm (Optimal)
    - 外壁数 (Wall Loops): 3 〜 4（ヒンジナックルの強度確保）
    - インフィル (Infill): 15% 〜 20%（ジャイロイド推奨）
    - サポート (Support): なし (None / 完全に不要)
    - アイロニング (Ironing): 最上面（Top surface）に適用すると画面がガラスのように滑らかになります
    - 印刷向き: 背面（Z=0 面）を下にして平置き配置

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
BODY_THICKNESS = 5.20               # 開いた時の完全フラット厚さ (5.20 mm)
CLOSED_WIDTH = 84.10                # 閉じた時の全幅
HALF_WIDTH = OVERALL_WIDTH_OPEN / 2.0  # 82.30 mm (片側ボディ幅)

# コーナーR (外観意匠)
CORNER_RADIUS_OUTER = 11.00         # iPhoneらしい外側コーナーR
CORNER_RADIUS_INNER = 1.00          # ヒンジ側コーナーR

# マルチカラー用スクリーンパーツ寸法 (1層分 0.20mm)
SCREEN_THICKNESS = 0.20             # スクリーンの層厚 (mm)

# 内側メインディスプレイ (7.6インチ相当)
MAIN_BEZEL_OUTER = 3.80             # 外周ベゼル幅
MAIN_BEZEL_HINGE = 3.00             # ヒンジ側ベゼル幅
MAIN_SCREEN_CORNER_R = 8.00         # メイン画面コーナーR

# 外側カバーディスプレイ (5.4インチ相当)
COVER_SCREEN_WIDTH = 73.00          # カバー画面幅
COVER_SCREEN_HEIGHT = 108.80        # カバー画面高さ
COVER_SCREEN_CORNER_R = 9.00        # カバー画面コーナーR

# ヒンジ幾何学 (1.75mmフィラメントピン軸)
PIN_DIAMETER = 2.00                 # 1.75mmフィラメント用ピン穴径
PIN_RADIUS = PIN_DIAMETER / 2.0     # 1.00 mm
HINGE_RADIUS = CLOSED_WIDTH - HALF_WIDTH  # 1.80 mm (84.10 - 82.30 = 1.80 mm)
PIVOT_Z = BODY_THICKNESS            # 5.20 mm (画面上面ツライチの回転中心)

NUM_SEGMENTS = 7                    # ナックル分割数
SEGMENT_PITCH = OVERALL_HEIGHT / NUM_SEGMENTS  # 約 16.83 mm
GAP_Y = 0.35                        # 軸方向クリアランス
GAP_RADIAL = 0.35                   # 半径方向クリアランス
CUTOUT_RADIUS = HINGE_RADIUS + GAP_RADIAL  # 2.15 mm (相手ナックルの受容半径)


# ============================================================
# モデリング関数
# ============================================================

def create_half_assembly(is_left: bool):
    """
    iPhone Duo の片側（ボディ本体およびツライチ密着スクリーンパーツ）を生成する。

    戻り値:
        body (Solid): ボディ本体
        main_screen (Solid): 内側メイン画面パーツ (厚さ 0.20mm)
        cover_screen (Solid or None): 外側カバー画面パーツ (左半身のみ)
    """
    # ----------------------------------------------------------
    # 1. 内側メインスクリーンパーツ (上面ツライチ: Z in [5.00, 5.20])
    # ----------------------------------------------------------
    scr_w = HALF_WIDTH - MAIN_BEZEL_OUTER - MAIN_BEZEL_HINGE
    scr_h = OVERALL_HEIGHT - 2 * MAIN_BEZEL_OUTER
    scr_cx = (-MAIN_BEZEL_HINGE - scr_w / 2.0) if is_left else (MAIN_BEZEL_HINGE + scr_w / 2.0)

    with BuildPart() as scr_bp:
        with BuildSketch(Plane.XY.offset(BODY_THICKNESS - SCREEN_THICKNESS)):
            with Locations([(scr_cx, 0)]):
                RectangleRounded(scr_w, scr_h, MAIN_SCREEN_CORNER_R)
        extrude(amount=SCREEN_THICKNESS)
    main_screen = scr_bp.part
    main_screen.label = "left_screen" if is_left else "right_screen"

    # ----------------------------------------------------------
    # 2. 外側カバースクリーンパーツ (左半身の底面ツライチ: Z in [0.00, 0.20])
    # ----------------------------------------------------------
    cover_screen = None
    if is_left:
        with BuildPart() as cov_bp:
            with BuildSketch(Plane.XY):
                cover_cx = -HALF_WIDTH / 2.0
                with Locations([(cover_cx, 0)]):
                    RectangleRounded(COVER_SCREEN_WIDTH, COVER_SCREEN_HEIGHT, COVER_SCREEN_CORNER_R)
            extrude(amount=SCREEN_THICKNESS)
        cover_screen = cov_bp.part
        cover_screen.label = "cover_screen"

    # ----------------------------------------------------------
    # 3. ボディ本体 (Z in [0, BODY_THICKNESS])
    # ----------------------------------------------------------
    with BuildPart() as body_bp:
        # 外形スケッチ
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

            # コーナーフィレット
            if is_left:
                v_outer = base_sk.vertices().sort_by(Axis.X)[:2]
                v_inner = base_sk.vertices().sort_by(Axis.X)[2:]
            else:
                v_inner = base_sk.vertices().sort_by(Axis.X)[:2]
                v_outer = base_sk.vertices().sort_by(Axis.X)[2:]
            fillet(v_outer, radius=CORNER_RADIUS_OUTER)
            fillet(v_inner, radius=CORNER_RADIUS_INNER)

        extrude(amount=BODY_THICKNESS)

        # スクリーンパーツの空間をくり抜く (完全密着・干渉ゼロにする)
        add(main_screen, mode=Mode.SUBTRACT)
        if cover_screen is not None:
            add(cover_screen, mode=Mode.SUBTRACT)

        # ----------------------------------------------------------
        # 4. ヒンジナックルの追加 (自分がナックルを持つセグメント)
        #    左半身: 偶数セグメント (0, 2, 4, 6)
        #    右半身: 奇数セグメント (1, 3, 5)
        # ----------------------------------------------------------
        my_segments = [i for i in range(NUM_SEGMENTS) if (i % 2 == 0) == is_left]
        other_segments = [i for i in range(NUM_SEGMENTS) if (i % 2 == 0) != is_left]

        y_start = -OVERALL_HEIGHT / 2.0

        for i in my_segments:
            y_seg_min = y_start + i * SEGMENT_PITCH + (GAP_Y / 2.0 if i > 0 else 0.0)
            y_seg_max = y_start + (i + 1) * SEGMENT_PITCH - (GAP_Y / 2.0 if i < NUM_SEGMENTS - 1 else 0.0)
            seg_len = y_seg_max - y_seg_min
            seg_center_y = (y_seg_min + y_seg_max) / 2.0

            # ナックル円筒
            with Locations([(0, seg_center_y, PIVOT_Z)]):
                Cylinder(radius=HINGE_RADIUS, height=seg_len, rotation=(90, 0, 0))

            # ナックル下部のブリッジ直方体 (底面 Z=0 まで一体化)
            bridge_x = -HINGE_RADIUS / 2.0 if is_left else HINGE_RADIUS / 2.0
            with Locations([(bridge_x, seg_center_y, BODY_THICKNESS / 2.0)]):
                Box(HINGE_RADIUS, seg_len, BODY_THICKNESS)

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

            # 相手ナックル回転時のスロット
            slot_x = -CUTOUT_RADIUS / 2.0 if is_left else CUTOUT_RADIUS / 2.0
            with Locations([(slot_x, seg_center_y, BODY_THICKNESS / 2.0)]):
                Box(CUTOUT_RADIUS, seg_len, BODY_THICKNESS + CUTOUT_RADIUS, mode=Mode.SUBTRACT)

        # ----------------------------------------------------------
        # 6. ピン軸貫通穴 (1.75mmフィラメント用 直径 2.0mm)
        # ----------------------------------------------------------
        with Locations([(0, 0, PIVOT_Z)]):
            Cylinder(radius=PIN_RADIUS, height=OVERALL_HEIGHT + 4.0, rotation=(90, 0, 0), mode=Mode.SUBTRACT)

    body = body_bp.part
    body.label = "left_body" if is_left else "right_body"

    return body, main_screen, cover_screen


def gen_step():
    """
    iPhone Duo のマルチカラー対応全パーツを生成し、アセンブリとして返す。
    CADスキルおよび Bambu Studio 連携用エントリーポイント。
    """
    left_body, left_screen, cover_screen = create_half_assembly(is_left=True)
    right_body, right_screen, _ = create_half_assembly(is_left=False)

    # アセンブリ構成
    all_parts = [left_body, left_screen, cover_screen, right_body, right_screen]
    assembly = Compound(all_parts, label="iphone_duo_mock")

    left_half = Compound([left_body, left_screen, cover_screen], label="iphone_duo_left")
    right_half = Compound([right_body, right_screen], label="iphone_duo_right")

    return assembly, left_half, right_half, all_parts


# ============================================================
# スクリプト直接実行時: STEPファイル出力とプレビュー
# ============================================================

if __name__ == "__main__":
    from ocp_vscode import show_object

    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("iPhone Duo マルチカラーフラットモックモデルを生成中...")
    assembly, left_half, right_half, all_parts = gen_step()

    # STEPファイル出力
    main_step_path = os.path.join(script_dir, "iphone_duo_mock.step")
    left_step_path = os.path.join(script_dir, "iphone_duo_left.step")
    right_step_path = os.path.join(script_dir, "iphone_duo_right.step")

    export_step(assembly, main_step_path)
    export_step(left_half, left_step_path)
    export_step(right_half, right_step_path)

    print(f"STEP (Full Assembly) 出力完了: {main_step_path}")
    print(f"STEP (Left Half Assembly) 出力完了: {left_step_path}")
    print(f"STEP (Right Half Assembly) 出力完了: {right_step_path}")

    # 寸法と干渉の最終検証
    left_solid = Compound([all_parts[0], all_parts[1], all_parts[2]])
    right_solid = Compound([all_parts[3], all_parts[4]])

    overlap = left_solid.intersect(right_solid)
    assert overlap is None, "エラー: 展開状態で左右パーツの干渉が検出されました。"

    # 180度折りたたみシミュレーション
    pivot_axis = Axis((0, 0, PIVOT_Z), (0, 1, 0))
    left_folded = left_solid.rotate(pivot_axis, 180)
    overlap_folded = left_folded.intersect(right_solid)
    assert overlap_folded is None, "エラー: 折りたたみ時に左右パーツの干渉が検出されました。"

    folded_comp = Compound([left_folded, right_solid])
    f_bbox = folded_comp.bounding_box()
    print(f"折りたたみ時寸法: 幅={f_bbox.size.X:.2f}mm (目標 84.1mm), 高さ={f_bbox.size.Y:.2f}mm (目標 117.8mm), 厚さ={f_bbox.size.Z:.2f}mm (目標 10.4〜11.3mm)")

    o_bbox = assembly.bounding_box()
    print(f"展開時寸法: 幅={o_bbox.size.X:.2f}mm (目標 164.6mm), 高さ={o_bbox.size.Y:.2f}mm (目標 117.8mm), 画面部厚さ={BODY_THICKNESS:.2f}mm (目標 5.2mm)")

    # プレビュー表示
    show_object(assembly, name="iphone_duo_mock")
