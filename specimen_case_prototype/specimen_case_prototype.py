import os
from build123d import *
from ocp_vscode import show_object

"""
設計要件:
    - 昆虫標本（国産カブトムシ等）用の高品位標本ケースのマスター設計。
    - 小型試作プレート（実寸 76.0mm × 127.0mm × 5.0mm）から、
      将来の大型プレート（200.0mm × 200.0mm × 5.0mm）まで、
      寸法数値を変更するだけで完全対応する堅牢なパラメトリック設計。
    - 0.6mmタングステンノズル ＋ Bambu PETG-CF（黒）での高強度・高速造形に完全最適化。
    - 45°テーパーによる完全サポートフリー（Bambu P2Sでサポート材なしで積層）。
    - 左右のガイド溝に深く噛み合う垂直落とし込み式エンドキャップ（抜け止めバー）により、
      縦置き展示でもアクリルが滑落せず、害虫の侵入を遮断する全周密閉構造。

推奨フィラメント & ノズル:
    - フィラメント: Bambu PETG-CF 黒 (Black)
    - ノズル: 0.6mm タングステンノズル (または硬化鋼ノズル)

推奨スライサー設定 (Bambu Studio - 0.6mmノズル向け):
    - ノズル径: 0.6mm
    - レイヤー高さ: 0.24mm〜0.28mm (0.24mm Standard推奨)
    - 壁面生成器 (Wall generator): Arachne (隙間のない可変線幅充填)
    - シーム位置 (Seam): 整列 (Aligned)
    - 壁ループ (Wall Loops): 3〜4
    - トップ/ボトムシェルレイヤー: 4〜5層
    - インフィル: 15%〜20% (Gyroid)
    - サポート: なし (None / 45°テーパーによりサポート完全不要)

将来の20cm×20cm大型化時の設定:
    - `ACRYLIC_WIDTH = 200.0`
    - `ACRYLIC_LENGTH = 200.0`
    - `WALL_THICKNESS = 3.6` (大型板の剛性確保のため推奨)
    - `RAIL_ENGAGEMENT = 3.0` (大型アクリルのたわみ防止のため推奨)
    ※上記のように数値を変更するだけで、自動的に最適な肉厚・クリアランス・溝深さにスケールします。

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# ==============================================================================
# パラメーター設定 (単位: mm)
# ==============================================================================

# --- アクリルプレート実寸 ---
# ※別ロットや20cm版を使う場合は、実測値に合わせて更新してください
ACRYLIC_WIDTH = 76.0        # 短辺 (X方向) ※20cm時は 200.0
ACRYLIC_LENGTH = 127.0      # 長辺 (Y方向) ※20cm時は 200.0
ACRYLIC_THICKNESS = 5.0     # 厚み (Z方向、実測値)

# --- 発泡スチロールボード・標本空間 ---
BOARD_THICKNESS = 5.0       # 底面発泡ボード（ペフ板）厚み
SPECIMEN_DEPTH = 40.0       # 標本有効深さ（ボード上面〜アクリル下面）

# --- ケース基本構造 ---
WALL_THICKNESS = 3.6        # ケース外壁の厚み (0.6mmノズル × 6周分で極めて頑丈)
BOTTOM_THICKNESS = 2.5      # 底面ベースの厚み
RAIL_ENGAGEMENT = 2.5       # レールのかかり代（左右・奥の溝深さ。20cm時は3.0推奨）
RAIL_LIP_THICKNESS = 2.5    # レール天井庇の厚み（Z方向）

# --- クリアランス（公差: 0.6mmノズル最適化値） ---
SLIDE_CLEARANCE_XY = 0.45   # 幅方向クリアランス (片側約 0.225mm)
SLIDE_CLEARANCE_Z = 0.35    # 厚み方向クリアランス (溝高さ = 5.35mm)
FIT_CLEARANCE = 0.15        # エンドキャップ等の高精度垂直嵌合クリアランス

# --- エンドキャップ（抜け止めバー） ---
CAP_GUIDE_DEPTH = 2.0       # 左右壁への食い込み深さ（外壁3.6mmに対し十分な深溝）
CAP_GUIDE_WIDTH = 2.4       # ガイド溝のY方向幅 (0.6mm × 4パスで均一充填)
NOTCH_WIDTH = 14.0          # 取り外し用指がかりノッチの幅
NOTCH_DEPTH = 1.2           # ノッチの深さ

# ==============================================================================
# 計算される派生寸法
# ==============================================================================

# アクリルが入るスロット寸法
SLOT_W = ACRYLIC_WIDTH + SLIDE_CLEARANCE_XY        # 76.45mm
SLOT_L = ACRYLIC_LENGTH + (SLIDE_CLEARANCE_XY / 2)  # 127.225mm
SLOT_H = ACRYLIC_THICKNESS + SLIDE_CLEARANCE_Z      # 5.35mm

# 標本・ボード空間の内寸（開口部）
INNER_W = SLOT_W - 2 * RAIL_ENGAGEMENT              # 71.45mm
INNER_L = SLOT_L - RAIL_ENGAGEMENT                  # 124.725mm
INNER_H = BOARD_THICKNESS + SPECIMEN_DEPTH          # 45.0mm

# ケース全体の総外寸
TOTAL_W = SLOT_W + 2 * WALL_THICKNESS               # 83.65mm
TOTAL_L = WALL_THICKNESS + SLOT_L + WALL_THICKNESS  # 134.425mm
TOTAL_H = BOTTOM_THICKNESS + INNER_H + SLOT_H + RAIL_LIP_THICKNESS  # 55.35mm

# 各高さ基準 (Z座標)
Z_BOTTOM = 0.0
Z_INNER_FLOOR = BOTTOM_THICKNESS                    # 2.5mm
Z_ACRYLIC_BOTTOM = Z_INNER_FLOOR + INNER_H          # 47.5mm (アクリル受け棚面)
Z_ACRYLIC_TOP = Z_ACRYLIC_BOTTOM + SLOT_H           # 52.85mm (アクリル上面)
Z_TOP = TOTAL_H                                     # 55.35mm (ケース天面)

# Y方向の各基準位置
Y_FRONT_OUTER = 0.0                                 # 手前外壁端面
Y_FRONT_INNER = WALL_THICKNESS                      # 手前内壁面 (アクリル前端)
Y_ACRYLIC_START = Y_FRONT_INNER                     # 3.6mm
Y_ACRYLIC_END = Y_ACRYLIC_START + SLOT_L            # 130.825mm (奥突き当て面)
Y_BACK_INNER = Y_ACRYLIC_END - RAIL_ENGAGEMENT      # 128.325mm (奥内壁面)
Y_BACK_OUTER = TOTAL_L                              # 134.425mm (奥外壁端面)


def build_case_body() -> Part:
    """
    標本ケース本体（case_body）を生成します。
    """
    with BuildPart() as case:
        # 1. 外形ブロックの作成
        Box(
            TOTAL_W,
            TOTAL_L,
            TOTAL_H,
            align=(Align.CENTER, Align.MIN, Align.MIN)
        )

        # 2. 標本＆底面ボードの内部キャビティ（空洞）を削る
        with Locations((0, Y_FRONT_INNER, Z_INNER_FLOOR)):
            Box(
                INNER_W,
                INNER_L,
                TOTAL_H - Z_INNER_FLOOR + 1.0,
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 3. アクリルスライド溝（スロット）を削る
        slot_cut_l = (Y_ACRYLIC_END - (-1.0))
        with Locations((0, -1.0, Z_ACRYLIC_BOTTOM)):
            Box(
                SLOT_W,
                slot_cut_l,
                SLOT_H,
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 4. 手前側開口部の上部貫通カット（エンドキャップ嵌合部＆スライド導入路）
        with Locations((0, -1.0, Z_ACRYLIC_TOP)):
            Box(
                SLOT_W,
                WALL_THICKNESS + 2.0,
                RAIL_LIP_THICKNESS + 1.0,
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 5. レール上部の45°テーパー（額縁風ベベル）
        t_w = RAIL_ENGAGEMENT
        t_h = RAIL_LIP_THICKNESS

        # 左側テーパー
        with BuildSketch(Plane.XZ.offset(Y_FRONT_INNER)) as sk_left:
            with Locations((-INNER_W / 2, Z_ACRYLIC_TOP)):
                Polygon(
                    (0, 0),
                    (-t_w, 0),
                    (0, t_h),
                    align=None
                )
        extrude(sk_left.sketch, amount=INNER_L + t_w, mode=Mode.SUBTRACT)

        # 右側テーパー
        with BuildSketch(Plane.XZ.offset(Y_FRONT_INNER)) as sk_right:
            with Locations((INNER_W / 2, Z_ACRYLIC_TOP)):
                Polygon(
                    (0, 0),
                    (t_w, 0),
                    (0, t_h),
                    align=None
                )
        extrude(sk_right.sketch, amount=INNER_L + t_w, mode=Mode.SUBTRACT)

        # 奥側テーパー (Y-Z平面)
        with BuildSketch(Plane.YZ.offset(-SLOT_W / 2 - 1.0)) as sk_back:
            with Locations((Y_BACK_INNER, Z_ACRYLIC_TOP)):
                Polygon(
                    (0, 0),
                    (t_w, 0),
                    (0, t_h),
                    align=None
                )
        extrude(sk_back.sketch, amount=SLOT_W + 2.0, mode=Mode.SUBTRACT)

        # 6. エンドキャップ用の垂直ガイド溝（左右壁の内側）
        guide_y = Y_FRONT_INNER / 2
        for side in [-1, 1]:
            with Locations((side * (SLOT_W / 2), guide_y, Z_ACRYLIC_BOTTOM)):
                Box(
                    CAP_GUIDE_DEPTH * 2,  # 壁への食い込み深さ
                    CAP_GUIDE_WIDTH,
                    TOTAL_H - Z_ACRYLIC_BOTTOM + 1.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT
                )

        # 7. 外側垂直エッジのフィレット（R2.0）
        vertical_edges = case.edges().filter_by(Axis.Z)
        outer_corners = [
            e for e in vertical_edges
            if abs(abs(e.center().X) - TOTAL_W / 2) < 0.2
        ]
        if outer_corners:
            fillet(outer_corners, radius=2.0)

    return case.part


def build_end_cap() -> Part:
    """
    手前開口部を塞ぎ、アクリル板の抜け落ちを物理的に防ぐエンドキャップ（end_cap）を生成します。
    """
    cap_w = SLOT_W - 2 * FIT_CLEARANCE
    cap_l = WALL_THICKNESS - 2 * FIT_CLEARANCE
    cap_h = TOTAL_H - Z_ACRYLIC_BOTTOM - FIT_CLEARANCE

    with BuildPart() as cap:
        # メインブロック
        Box(
            cap_w,
            cap_l,
            cap_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN)
        )

        # 左右のガイドリブ（外側の溝端までしっかり届く頑丈な突起）
        # 本体の溝外側端は ±(SLOT_W/2 + CAP_GUIDE_DEPTH)
        rib_reach_x = (SLOT_W / 2 + CAP_GUIDE_DEPTH) - FIT_CLEARANCE
        rib_width = (rib_reach_x - (cap_w / 2)) * 2
        rib_len = CAP_GUIDE_WIDTH - 2 * FIT_CLEARANCE
        for side in [-1, 1]:
            with Locations((side * (cap_w / 2), 0, 0)):
                Box(
                    rib_width,
                    rib_len,
                    cap_h,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.ADD
                )

        # 取り外し用の指がかりノッチ
        with Locations((0, 0, cap_h)):
            Box(
                NOTCH_WIDTH,
                cap_l + 2.0,
                NOTCH_DEPTH * 2,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                mode=Mode.SUBTRACT
            )

        # 上部角の微小面取り
        top_edges = cap.edges().sort_by(Axis.Z)[-4:]
        if top_edges:
            chamfer(top_edges, length=0.4)

    return cap.part


# ==============================================================================
# 実行とエクスポート
# ==============================================================================
if __name__ == "__main__":
    print("Building master specimen case model...")
    case_body = build_case_body()
    end_cap = build_end_cap()

    print(f"Master Case Body Bounding Box: {case_body.bounding_box()}")
    print(f"Master End Cap Bounding Box: {end_cap.bounding_box()}")

    # アセンブリ配置: ワンプレート印刷
    placed_cap = end_cap.moved(Location((TOTAL_W / 2 + 18.0, Y_FRONT_INNER / 2, 0)))
    assembly = Compound(children=[case_body, placed_cap])

    output_dir = os.path.dirname(__file__)
    output_path = os.path.join(output_dir, "specimen_case_prototype.step")

    export_step(assembly, output_path)
    print(f"Successfully exported Master STEP to: {output_path}")

    try:
        show_object(case_body, name="case_body")
        show_object(placed_cap, name="end_cap")
    except Exception:
        pass
