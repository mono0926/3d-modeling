import os
from build123d import *
from ocp_vscode import show_object

"""
設計要件:
    - 昆虫標本（国産カブトムシ等）用の高品位標本ケースのプロトタイプ。
    - アクリルプレート（実寸 76.0mm × 127.0mm × 5.0mm）および底面発泡スチロールボード（厚さ5.0mm）と組み合わせる。
    - 大型オスのカブトムシを昆虫針で固定しても干渉しない有効深さ（40.0mm）を確保。
    - アクリル板は短辺側から長辺方向へスライド挿入する方式。
    - スライド溝の上部を45°テーパー（額縁風ベベル）とすることで、FDM印刷時のオーバーハング垂れ下がりを防止（完全サポートフリー）。
    - 手前開口部には垂直落とし込み式のエンドキャップ（抜け止めバー）を配置し、縦置き展示でもアクリルが滑落せず、微細害虫の侵入を遮断する全周密閉構造。
    - 手前壁・奥壁・左右壁の全周が底面から強固に立ち上がり、エンドキャップ装着時は外壁が全周ツライチになる洗練された外観。
    - 将来的に 200mm × 200mm 等の大型アクリルプレートにも数値を変更するだけで対応可能な完全パラメトリック設計。

推奨フィラメント:
    - Bambu PETG-CF 黒 (Black)
    - 理由: 優れた高剛性・低熱収縮率（PLA同等）、積層痕が目立たない高級感のあるマットブラックな質感。

推奨スライサー設定 (Bambu Studio):
    - ノズル径: 0.4mm
    - レイヤー高さ: 0.20mm Standard
    - 壁ループ (Wall Loops): 4 (剛性と気密性を確保)
    - トップ/ボトムシェルレイヤー: 5層
    - インフィル: 15%〜20% (Gyroid)
    - サポート: なし (None / 45°テーパー設計により完全サポートフリー)
    - シーム位置 (Seam): 背面（Back）または整列（Aligned）

印刷統計（予想）:
    - case_body: 印刷時間 約2時間40分、フィラメント使用量 約125g
    - end_cap: 印刷時間 約8分、フィラメント使用量 約4g

パラメーター変更ガイド:
    - アクリル板の実寸測定は必須です。ロットや切り出しにより厚み（4.8〜5.2mm）や外寸に誤差がある場合、
      以下の定数 `ACRYLIC_WIDTH`, `ACRYLIC_LENGTH`, `ACRYLIC_THICKNESS` を実測値に合わせて更新してください。
    - スライドが硬い場合は `SLIDE_CLEARANCE_XY` や `SLIDE_CLEARANCE_Z` を 0.05mm 単位で広げてください。
    - 将来の20cm×20cm化時は `ACRYLIC_WIDTH = 200.0`, `ACRYLIC_LENGTH = 200.0` に変更するだけで自動スケールします。

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# ==============================================================================
# パラメーター設定 (単位: mm)
# ==============================================================================

# --- アクリルプレート実寸 ---
ACRYLIC_WIDTH = 76.0        # 短辺 (X方向)
ACRYLIC_LENGTH = 127.0      # 長辺 (Y方向)
ACRYLIC_THICKNESS = 5.0     # 厚み (Z方向、実測値)

# --- 発泡スチロールボード・標本空間 ---
BOARD_THICKNESS = 5.0       # 底面発泡ボード（ペフ板）厚み
SPECIMEN_DEPTH = 40.0       # 標本有効深さ（ボード上面〜アクリル下面）

# --- ケース基本構造 ---
WALL_THICKNESS = 3.0        # ケース外壁の厚み
BOTTOM_THICKNESS = 2.5      # 底面ベースの厚み
RAIL_ENGAGEMENT = 2.5       # レールのかかり代（左右・奥の溝の深さ）
RAIL_LIP_THICKNESS = 2.5    # レール天井庇の厚み（Z方向）

# --- クリアランス（公差） ---
SLIDE_CLEARANCE_XY = 0.3    # 幅方向クリアランス (片側 0.15mm)
SLIDE_CLEARANCE_Z = 0.25    # 厚み方向クリアランス (溝高さ = 5.25mm)
FIT_CLEARANCE = 0.15        # エンドキャップ等の垂直嵌合クリアランス

# --- エンドキャップ（抜け止めバー） ---
CAP_GUIDE_DEPTH = 1.5       # 左右壁への食い込み深さ（リブ幅）
CAP_GUIDE_WIDTH = 2.0       # ガイド溝のY方向幅
NOTCH_WIDTH = 14.0          # 取り外し用指がかりノッチの幅
NOTCH_DEPTH = 1.2           # ノッチの深さ

# ==============================================================================
# 計算される派生寸法
# ==============================================================================

# アクリルが入るスロット寸法
SLOT_W = ACRYLIC_WIDTH + SLIDE_CLEARANCE_XY        # 76.3mm
SLOT_L = ACRYLIC_LENGTH + (SLIDE_CLEARANCE_XY / 2)  # 127.15mm
SLOT_H = ACRYLIC_THICKNESS + SLIDE_CLEARANCE_Z      # 5.25mm

# 標本・ボード空間の内寸（開口部）
INNER_W = SLOT_W - 2 * RAIL_ENGAGEMENT              # 71.3mm
INNER_L = SLOT_L - RAIL_ENGAGEMENT                  # 124.65mm
INNER_H = BOARD_THICKNESS + SPECIMEN_DEPTH          # 45.0mm

# ケース全体の総外寸
TOTAL_W = SLOT_W + 2 * WALL_THICKNESS               # 82.3mm
TOTAL_L = WALL_THICKNESS + SLOT_L + WALL_THICKNESS  # 133.15mm
TOTAL_H = BOTTOM_THICKNESS + INNER_H + SLOT_H + RAIL_LIP_THICKNESS  # 55.25mm

# 各高さ基準 (Z座標)
Z_BOTTOM = 0.0
Z_INNER_FLOOR = BOTTOM_THICKNESS                    # 2.5mm
Z_ACRYLIC_BOTTOM = Z_INNER_FLOOR + INNER_H          # 47.5mm (アクリル受け棚面)
Z_ACRYLIC_TOP = Z_ACRYLIC_BOTTOM + SLOT_H           # 52.75mm (アクリル上面)
Z_TOP = TOTAL_H                                     # 55.25mm (ケース天面)

# Y方向の各基準位置
Y_FRONT_OUTER = 0.0                                 # 手前外壁端面
Y_FRONT_INNER = WALL_THICKNESS                      # 手前内壁面 (アクリル前端)
Y_ACRYLIC_START = Y_FRONT_INNER                     # 3.0mm
Y_ACRYLIC_END = Y_ACRYLIC_START + SLOT_L            # 130.15mm (奥突き当て面)
Y_BACK_INNER = Y_ACRYLIC_END - RAIL_ENGAGEMENT      # 127.65mm (奥内壁面)
Y_BACK_OUTER = TOTAL_L                              # 133.15mm (奥外壁端面)


def build_case_body() -> Part:
    """
    標本ケース本体（case_body）を生成します。
    """
    with BuildPart() as case:
        # 1. 外形ブロックの作成
        # 原点: Xは中心(0)、Yは手前(0)、Zは底面(0)
        Box(
            TOTAL_W,
            TOTAL_L,
            TOTAL_H,
            align=(Align.CENTER, Align.MIN, Align.MIN)
        )

        # 2. 標本＆底面ボードの内部キャビティ（空洞）を削る
        # Y位置: 手前内壁(Y_FRONT_INNER)から奥内壁(Y_BACK_INNER)まで
        with Locations((0, Y_FRONT_INNER, Z_INNER_FLOOR)):
            Box(
                INNER_W,
                INNER_L,
                TOTAL_H - Z_INNER_FLOOR + 1.0,  # 上までくり抜き
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 3. アクリルスライド溝（スロット）を削る
        # Z: Z_ACRYLIC_BOTTOM から Z_ACRYLIC_TOP まで
        # Y: 手前外壁を貫通(Y = -1.0)から奥突き当て(Y_ACRYLIC_END)まで
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
        # 手前壁 (Y = 0 から Y_FRONT_INNER) のうち、Z_ACRYLIC_TOP から天面までを開放
        with Locations((0, -1.0, Z_ACRYLIC_TOP)):
            Box(
                SLOT_W,
                WALL_THICKNESS + 2.0,
                RAIL_LIP_THICKNESS + 1.0,
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT
            )

        # 5. レール上部の45°テーパー（額縁風ベベル）
        # スロット上部 (Z_ACRYLIC_TOP) から 天面 (Z_TOP) にかけて、
        # 内側に向かって45°で立ち上がる庇の下面テーパーをカット。
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
        # 手前内壁 (Y = Y_FRONT_INNER) の直前位置に垂直な溝を左右壁に掘る
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
        # 奥の角および手前の角
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
        # メインブロック（手前壁の上部開口を埋めるブロック）
        Box(
            cap_w,
            cap_l,
            cap_h,
            align=(Align.CENTER, Align.CENTER, Align.MIN)
        )

        # 左右のガイドリブ（垂直キー突起）
        rib_w = (CAP_GUIDE_DEPTH - FIT_CLEARANCE) * 2
        rib_l = CAP_GUIDE_WIDTH - 2 * FIT_CLEARANCE
        for side in [-1, 1]:
            with Locations((side * (cap_w / 2), 0, 0)):
                Box(
                    rib_w,
                    rib_l,
                    cap_h,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.ADD
                )

        # 取り外し用の指がかりノッチ（上面中央の窪み）
        with Locations((0, 0, cap_h)):
            Box(
                NOTCH_WIDTH,
                cap_l + 2.0,
                NOTCH_DEPTH * 2,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                mode=Mode.SUBTRACT
            )

        # 上部角の微小面取り (0.4mm) で手触りと高級感を向上
        top_edges = cap.edges().sort_by(Axis.Z)[-4:]
        if top_edges:
            chamfer(top_edges, length=0.4)

    return cap.part


# ==============================================================================
# 実行とエクスポート
# ==============================================================================
if __name__ == "__main__":
    print("Building specimen case prototype...")
    case_body = build_case_body()
    end_cap = build_end_cap()

    print(f"Case Body Bounding Box: {case_body.bounding_box()}")
    print(f"End Cap Bounding Box: {end_cap.bounding_box()}")

    # アセンブリ配置: スライサーでワンプレート印刷できるよう、本体の右側にエンドキャップを並べて配置
    placed_cap = end_cap.moved(Location((TOTAL_W / 2 + 18.0, Y_FRONT_INNER / 2, 0)))
    assembly = Compound(children=[case_body, placed_cap])

    # 出力パス設定
    output_dir = os.path.dirname(__file__)
    output_path = os.path.join(output_dir, "specimen_case_prototype.step")

    export_step(assembly, output_path)
    print(f"Successfully exported STEP to: {output_path}")

    # VS Code / GUI プレビュー用
    try:
        show_object(case_body, name="case_body")
        show_object(placed_cap, name="end_cap")
    except Exception:
        pass
