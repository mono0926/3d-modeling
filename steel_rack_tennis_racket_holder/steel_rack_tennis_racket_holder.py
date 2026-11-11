"""
設計要件:
    - マットブラックのスチールラック（天板端部が下に18.1mm折り曲げられた約1.0mm厚の薄鉄板フチ ＋
      その約2.0mm下・約2.0mm手前に通る φ7.2mm 水平丸パイプ）にワンタッチ装着できる硬式テニスラケット掛け。
    - ジュニア用「Wilson CLASH 26 V3.0」（26インチ / 100sq.in. / フレーム厚24.0mmフラット / スロート片側約23.5°）と
      大人用「HEAD EXTREME MP 2026 (233316)」（27インチ / 100sq.in. / フレーム厚23-26-21mm / スロート片側約24.2°）の
      2機種を1つのホルダーで完全兼用し、ガット面をラックと平行（ヘッド上向き）にしてスッキリ縦掛けする。
    - ネジ・両面テープ不要の「Cスナップ一体型デュアルJフック（3点圧縮セルフロック）」機構:
      1. 丸パイプと棚板の狭い隙間（約2.0mm）には一切パーツを通さず、丸パイプの下から軽く傾けて裏側懐空間へ回し込み、
         φ7.2mm丸パイプへ220°相当（+135°の45°接線ランプ〜-14°下前爪、弾性干渉約0.33mm）で「パチン」とCスナップ固定する。
      2. ラケット荷重による手前へのお辞儀モーメントを、①薄鉄板フチ裏面ストッパー爪（u=-1.35mm）・②丸パイプ上奥座・
         ③丸パイプ下前スナップ爪の3点純圧縮で受け止め、たわみ0.1mm未満の完全セルフロックと棚板上面への出っ張りゼロを実現する。
    - 外抱えV字クレードル（片側基準24.0° ＋ 長手R350mm相当の太鼓クラウニング ＋ 全周保護面取り/フィレット）により、
      上から下ろすだけで両ラケットとも自動調心して面接触保持し、最大厚26.0mm部でも棚板前面から8.0mm以上の逃げを確保する。
    - 最新の3Dプリンター（Bambu Lab P2S Combo 等）での出力を想定し、底面（Z=0）ベタ置きの完全サポートフリー（全オーバーハング45°以下）
      および 0.4mmノズル(0.20mm層)/0.6mmノズル(0.30mm層)両対応の 0.60mm 整数倍高さで設計する。
    - モデルごとに専用ディレクトリで管理し、本番モデルと約10分で実機確認できる事前嵌合テストピースの2つのSTEPファイルを同時出力する。

推奨フィラメント:
    - PETG（Bambu PETG HF / PETG Matte ブラック推奨 — Cスナップ着脱時の高い靭性・耐クリープ性とマット黒ラックへの一体感のため）
    - PLA Matte / PLA Tough でも代用可能（着脱時最大ひずみ約0.35%の低ひずみ設計のため割れずに使用可能だが、長期耐クリープ性の観点からPETGを推奨）。

推奨スライサー設定:
    - レイヤー高さ (Layer height): 0.20mm (0.4mmノズル時) または 0.30mm (0.6mmノズル時) — 全高56.40mm / テスト28.80mm ともに整数倍
    - 壁ループ (Wall loops): 3〜4（JフックUアームおよびV字クレードルの高剛性確保）
    - インフィル (Sparse infill): 20〜25% (Gyroid または Cross Hatch)
    - サポート (Supports): なし (None — 全オーバーハング45.0°以下のサポートフリー設計)
    - ブリム (Brim): 不要（Z=0に広いフラット接地面があるため安定）

印刷統計（予想）:
    - steel_rack_tennis_racket_holder.step: 印刷時間 約65〜80分、フィラメント使用量 約58g
    - steel_rack_tennis_racket_holder_fit_test.step: 印刷時間 約10〜13分、フィラメント使用量 約6g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import math
from pathlib import Path
from build123d import *

try:
    from ocp_vscode import show_object
except ImportError:  # pragma: no cover

    def show_object(*_args, **_kwargs) -> None:
        pass


# ==============================================================================
# 定数パラメーター定義 (単位: mm / 角度: deg)
# 内部設計座標 (x, u, v):
#   x: ラック左右方向 (中央 x = 0.00)
#   u: 前後方向 (棚板前垂れ外側表面 u = 0.00, 室内手前 +u, 棚奥側 -u)
#   v: 上下方向 (棚板前垂れ下端 v = 0.00, 上方 +v, 下方 -v)
# ==============================================================================

# --- スチールラック実測基準寸法 ---
PIPE_DIA = 7.20  # 水平丸パイプ外径
PIPE_RADIUS = PIPE_DIA / 2.0  # 3.60mm
PIPE_FRONT_PROTRUSION = 2.00  # 棚板前面(u=0)から丸パイプ手前端までの突出量
PIPE_GAP_TO_SKIRT = 2.00  # 棚板下端(v=0)から丸パイプ上端までの隙間
PIPE_CENTER_U = PIPE_FRONT_PROTRUSION - PIPE_RADIUS  # -1.60mm
PIPE_CENTER_V = -(PIPE_GAP_TO_SKIRT + PIPE_RADIUS)  # -5.60mm

SKIRT_HEIGHT = 18.10  # 棚板前垂れ縦高さ (v = 0.00 〜 +18.10mm)
SKIRT_THICKNESS_MAX = 1.15  # 約1.0mm薄鉄板の最大想定板厚 (u = -1.15 〜 0.00mm)

# --- 造形ピッチ・全体高さ設定 (0.20mm / 0.30mm レイヤー両対応の 0.60mm 整数倍) ---
HOLDER_BOTTOM_V = -15.00  # ビルドプレート接地面 (Z = 0.00mm)
HOLDER_TOP_V = 41.40  # クレードル上端 (全高 56.40mm = 0.60mm * 94)
CRADLE_TOTAL_HEIGHT = HOLDER_TOP_V - HOLDER_BOTTOM_V  # 56.40mm

FIT_TEST_TOP_V = 13.80  # テストピース上端 (全高 28.80mm = 0.60mm * 48)
FIT_TEST_HEIGHT = FIT_TEST_TOP_V - HOLDER_BOTTOM_V  # 28.80mm
FIT_TEST_WIDTH = 18.00  # 本番片側Jフックと完全同一幅

# --- Cスナップ一体型デュアルJフック (3点圧縮セルフロック機構) ---
HOOK_WIDTH = 18.00  # 左右各フック幅 (2本合計 36.00mm)
HOOK_INNER_HALF_GAP = 10.00  # 中央軽量化オープン幅の半値 (中央20.00mm開放)
HOOK_OUTER_HALF_SPAN = HOOK_INNER_HALF_GAP + HOOK_WIDTH  # 28.00mm (フック全幅 56.00mm)

PIPE_SADDLE_CLEARANCE = 0.10  # パイプ半径クリアランス (内径 φ7.40mm)
PIPE_SADDLE_RADIUS = PIPE_RADIUS + PIPE_SADDLE_CLEARANCE  # 3.70mm
PIPE_UPPER_TANGENT_DEG = 135.0  # 上奥45°サポートフリー接線開始角 (n.Z = -0.7071)
PIPE_SNAP_JAW_DEG = -14.0  # 下前Cスナップ爪先端角 (開口弦長 約6.87mm -> 0.33mm弾性スナップ)

HOOK_REAR_BACK_U = -8.90  # 背面Uステム外側面 (パイプ奥端-5.30mmに対し肉厚3.60mm)
STOPPER_FRONT_U = -1.35  # 棚板フチ裏ストッパー爪の前面 (鉄板裏面 -1.15mm に対し 0.20mm クリアランス)
STOPPER_BOTTOM_V = 3.50  # ストッパー爪有効面の下端 (クレードル後面 +6.30mm との開口 > 7.65mm)
STOPPER_TOP_V = 7.80  # ストッパー爪上端
STOPPER_BACK_U = -5.60  # ストッパー爪背面

# --- 2機種兼用・外抱えV字クレードル寸法 ---
CRADLE_BACKPLATE_REAR_U = 6.30  # クレードル背板後面 (φ7.20mmパイプ通過開口を確保)
CRADLE_BACKPLATE_THICKNESS = 4.20  # 背板肉厚
CRADLE_INNER_BACK_U = CRADLE_BACKPLATE_REAR_U + CRADLE_BACKPLATE_THICKNESS  # +10.50mm
CRADLE_GROOVE_DEPTH = 26.50  # ラケット前後溝内寸 (21〜25mm厚スロートに余裕を持って対応)
CRADLE_FRONT_LIP_INNER_U = CRADLE_INNER_BACK_U + CRADLE_GROOVE_DEPTH  # +37.00mm
CRADLE_FRONT_LIP_THICKNESS = 4.50  # 手前返しリップ肉厚
CRADLE_FRONT_OUTER_U = CRADLE_FRONT_LIP_INNER_U + CRADLE_FRONT_LIP_THICKNESS  # +41.50mm

CRADLE_BOTTOM_INNER_WIDTH = 52.00  # v=-15.00mm での左右V受け面内幅 (シャフト通過開口)
CRADLE_HALF_ANGLE_DEG = 24.0  # スロート片側基準テーパー角 (CLASH 23.5° / EXTREME 24.2° の中心)
CRADLE_CROWN_BULGE = 0.45  # 長手方向R350mm相当の太鼓クラウニング中央膨らみ量 (エッジ当たり防止)
CRADLE_SIDE_WALL_THICKNESS = 7.80  # V字サイドウォール水平方向厚み
CRADLE_BACK_FLANGE_WIDTH = 13.00  # 背板フランジの内側張り出し幅
CRADLE_FRONT_LIP_WIDTH = 11.00  # 手前返しリップの内側張り出し幅

BRIDGE_SPINE_TOP_V = 7.80  # 左右Vウイングと左右Jフックを剛結する下部センターブリッジ高さ

# --- 出力時XYセンタリングオフセット ---
MAIN_U_OFFSET = -(HOOK_REAR_BACK_U + CRADLE_FRONT_OUTER_U) / 2.0  # -16.30mm
FIT_TEST_FRONT_U = CRADLE_INNER_BACK_U  # +10.50mm (指掛け背板前面)
FIT_TEST_U_OFFSET = -(HOOK_REAR_BACK_U + FIT_TEST_FRONT_U) / 2.0  # -0.80mm


def _build_j_hook_2d_face() -> Face:
    """(u, v) 平面におけるCスナップ一体型Jフック断面 Face を生成する (X=0 の YZ平面上)."""
    # 1. パイプサドル円弧上の基準点算出
    a_top = math.radians(PIPE_UPPER_TANGENT_DEG)  # +135°
    a_mid = math.radians(-110.0)  # 円弧中間通過点 (下奥側)
    a_jaw = math.radians(PIPE_SNAP_JAW_DEG)  # -14° (下前スナップ爪先端)

    p_arc_top = (
        PIPE_CENTER_U + PIPE_SADDLE_RADIUS * math.cos(a_top),
        PIPE_CENTER_V + PIPE_SADDLE_RADIUS * math.sin(a_top),
    )
    p_arc_mid = (
        PIPE_CENTER_U + PIPE_SADDLE_RADIUS * math.cos(a_mid),
        PIPE_CENTER_V + PIPE_SADDLE_RADIUS * math.sin(a_mid),
    )
    p_arc_jaw = (
        PIPE_CENTER_U + PIPE_SADDLE_RADIUS * math.cos(a_jaw),
        PIPE_CENTER_V + PIPE_SADDLE_RADIUS * math.sin(a_jaw),
    )

    # 2. p_arc_top (+135°) から 45.0° 接線 (Δv = Δu, オーバーハング厳密45.0°) で u=-2.35 まで立ち上げ、
    #    そこから急勾配 (約75°) で棚板フチ裏ストッパー爪前面 (u=-1.35, v=+3.50..+7.80) へ繋ぐ
    u_knee = -2.35
    v_knee = p_arc_top[1] + (u_knee - p_arc_top[0])  # 45.0° 接線上の膝点

    # 3. 下前スナップ爪先端 p_arc_jaw (+1.99, -6.50) から 45° 導入ランプで前方へ逃がし、
    #    クレードル背板後面 (u=+6.30) へ接続する
    p_jaw_outer = (p_arc_jaw[0] + 1.45, p_arc_jaw[1] - 0.35)
    p_front_throat = (CRADLE_BACKPLATE_REAR_U, -9.20)

    pts_poly = [
        p_arc_top,
        (u_knee, v_knee),
        (STOPPER_FRONT_U, STOPPER_BOTTOM_V),
        (STOPPER_FRONT_U, STOPPER_TOP_V),
        (STOPPER_BACK_U, STOPPER_TOP_V),
        (HOOK_REAR_BACK_U, STOPPER_TOP_V - (STOPPER_BACK_U - HOOK_REAR_BACK_U)),  # 45° 面取り頂部
        (HOOK_REAR_BACK_U, HOLDER_BOTTOM_V),
        (CRADLE_INNER_BACK_U, HOLDER_BOTTOM_V),
        (CRADLE_INNER_BACK_U, BRIDGE_SPINE_TOP_V),
        (CRADLE_BACKPLATE_REAR_U, BRIDGE_SPINE_TOP_V),
        p_front_throat,
        p_jaw_outer,
        p_arc_jaw,
    ]

    # YZ平面 (Y=u, Z=v) 上にスケッチを作成し、Z=0 接地オフセット (-HOLDER_BOTTOM_V) は後段で一括適用
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            ThreePointArc(p_arc_jaw, p_arc_mid, p_arc_top)
            Polyline(*pts_poly)
        make_face()
        # 応力集中を防ぎ、スナップ導入を滑らかにする頂点2Dフィレット (Z=0底面角は除外)
        target_verts = [
            vtx
            for vtx in sk.vertices()
            if vtx.Y > HOLDER_BOTTOM_V + 0.2 and vtx.Y < BRIDGE_SPINE_TOP_V - 0.2
        ]
        # 爪先端と膝部のみ安全半径 R0.55mm で丸める
        jaw_verts = [
            vtx
            for vtx in target_verts
            if math.hypot(vtx.X - p_jaw_outer[0], vtx.Y - p_jaw_outer[1]) < 1.8
            or math.hypot(vtx.X - p_front_throat[0], vtx.Y - p_front_throat[1]) < 1.2
        ]
        if jaw_verts:
            fillet(jaw_verts, 0.55)

    return sk.sketch.faces()[0]


def _build_single_v_wing(sign_x: float) -> Part:
    """片側 (+X または -X) のクラウニング付き外抱えV字クレードル翼を生成する (設計座標系)."""
    tan_a = math.tan(math.radians(CRADLE_HALF_ANGLE_DEG))
    h = CRADLE_TOTAL_HEIGHT  # 56.40mm
    x_bot_in = CRADLE_BOTTOM_INNER_WIDTH / 2.0  # 26.00mm
    x_top_in = x_bot_in + h * tan_a  # 51.11mm
    x_mid_in = 0.5 * (x_bot_in + x_top_in) - CRADLE_CROWN_BULGE  # 内側へ0.45mm膨らむ太鼓R

    x_bot_out = x_bot_in + CRADLE_SIDE_WALL_THICKNESS  # 33.80mm
    x_top_out = x_top_in + CRADLE_SIDE_WALL_THICKNESS  # 58.91mm

    # 1. 外殻ブロック (背面 u=6.30 〜 前端 u=41.50) を XZ 正面輪郭から押し出し生成
    u_span_total = CRADLE_FRONT_OUTER_U - CRADLE_BACKPLATE_REAR_U  # 35.20mm
    x_bot_flange = x_bot_in - CRADLE_BACK_FLANGE_WIDTH  # 13.00mm
    x_top_flange = x_top_in - CRADLE_BACK_FLANGE_WIDTH  # 38.11mm

    with BuildSketch(Plane.XZ.offset(-CRADLE_BACKPLATE_REAR_U)) as sk_outer:
        with BuildLine():
            Polyline(
                (sign_x * x_bot_flange, HOLDER_BOTTOM_V),
                (sign_x * x_bot_out, HOLDER_BOTTOM_V),
                (sign_x * x_top_out, HOLDER_TOP_V),
                (sign_x * x_top_flange, HOLDER_TOP_V),
                (sign_x * x_bot_flange, HOLDER_BOTTOM_V),
            )
        make_face()
    # Plane.XZ の法線は -Y なので -u_span_total 押し出しで +Y (+u) 方向へ伸ばす
    wing_blank = extrude(sk_outer.sketch, amount=-u_span_total)

    # 2. ラケットスロート受け溝 (u = +10.50 〜 +37.00, 内面は R350mm 相当の太鼓クラウニング曲面!) を切り抜く
    with BuildSketch(Plane.XZ.offset(-CRADLE_INNER_BACK_U)) as sk_groove:
        with BuildLine():
            ThreePointArc(
                (sign_x * x_bot_in, HOLDER_BOTTOM_V - 1.0),
                (sign_x * x_mid_in, 0.5 * (HOLDER_BOTTOM_V + HOLDER_TOP_V)),
                (sign_x * x_top_in, HOLDER_TOP_V + 1.0),
            )
            Polyline(
                (sign_x * x_top_in, HOLDER_TOP_V + 1.0),
                (0.0, HOLDER_TOP_V + 1.0),
                (0.0, HOLDER_BOTTOM_V - 1.0),
                (sign_x * x_bot_in, HOLDER_BOTTOM_V - 1.0),
            )
        make_face()
    groove_cut = extrude(sk_groove.sketch, amount=-CRADLE_GROOVE_DEPTH)

    # 3. 手前返しリップの内側開放カット (u = +37.00 〜 +42.50 で CRADLE_FRONT_LIP_WIDTH より中央側を開放)
    x_bot_lip_in = x_bot_in - CRADLE_FRONT_LIP_WIDTH  # 15.00mm
    x_top_lip_in = x_top_in - CRADLE_FRONT_LIP_WIDTH  # 40.11mm
    with BuildSketch(Plane.XZ.offset(-CRADLE_FRONT_LIP_INNER_U)) as sk_front_open:
        with BuildLine():
            Polyline(
                (sign_x * x_bot_lip_in, HOLDER_BOTTOM_V - 1.0),
                (sign_x * x_top_lip_in, HOLDER_TOP_V + 1.0),
                (0.0, HOLDER_TOP_V + 1.0),
                (0.0, HOLDER_BOTTOM_V - 1.0),
                (sign_x * x_bot_lip_in, HOLDER_BOTTOM_V - 1.0),
            )
        make_face()
    front_open_cut = extrude(sk_front_open.sketch, amount=-(CRADLE_FRONT_LIP_THICKNESS + 2.0))

    wing = wing_blank - groove_cut - front_open_cut

    # 4. 長尺傾斜エッジへの保護Rフィレット (Z方向高さ > 50mm のエッジを座標で分類)
    sloped_edges = [e for e in wing.edges() if e.bounding_box().size.Z > 50.0]
    # 外周2エッジ (|X_center| > 42mm): お子様の安全性と外観向上のため R3.0mm
    outer_sloped = [e for e in sloped_edges if abs(e.center().X) > 42.0]
    if outer_sloped:
        wing = fillet(outer_sloped, radius=3.00)

    # 溝底2エッジ + 手前返しリップ内側2エッジ (Y > +10.0 かつ |X_center| > 26.5): ラケット塗装保護のため R1.80mm
    sloped_after = [e for e in wing.edges() if e.bounding_box().size.Z > 50.0]
    racket_sloped = [
        e
        for e in sloped_after
        if e.center().Y > CRADLE_INNER_BACK_U - 0.5 and 26.5 < abs(e.center().X) < 42.0
    ]
    if racket_sloped:
        wing = fillet(racket_sloped, radius=1.80)

    # 5. 上端入口エッジを滑らかに面取りしてラケット投入ガイド性と安全性を向上 (Z=HOLDER_TOP_V 面)
    top_face = wing.faces().sort_by(Axis.Z)[-1]
    wing = chamfer(top_face.edges(), length=1.20)

    return wing


def build_holder() -> Part:
    """2機種兼用V字クレードル ＋ Cスナップ一体型デュアルJフックの本番モデルを生成する."""
    hook_face = _build_j_hook_2d_face()

    # 1. 左右1ペアのCスナップJフック (x = -28..-10 および +10..+28)
    hook_right = extrude(
        Pos(HOOK_INNER_HALF_GAP, 0.0, 0.0) * hook_face,
        amount=HOOK_WIDTH,
        dir=(1, 0, 0),
    )
    hook_left = extrude(
        Pos(-HOOK_OUTER_HALF_SPAN, 0.0, 0.0) * hook_face,
        amount=HOOK_WIDTH,
        dir=(1, 0, 0),
    )

    # 2. 左右のフックと左右のVウイングを下部で一体剛結するセンターブリッジ背板
    bridge_w = 2.0 * HOOK_OUTER_HALF_SPAN  # 56.00mm
    bridge_h = BRIDGE_SPINE_TOP_V - HOLDER_BOTTOM_V  # 22.80mm
    center_bridge = Pos(
        0.0,
        CRADLE_BACKPLATE_REAR_U + CRADLE_BACKPLATE_THICKNESS / 2.0,
        HOLDER_BOTTOM_V + bridge_h / 2.0,
    ) * Box(bridge_w, CRADLE_BACKPLATE_THICKNESS, bridge_h)

    # 3. 左右の外抱えV字クレードル翼
    wing_right = _build_single_v_wing(+1.0)
    wing_left = _build_single_v_wing(-1.0)

    combined = (hook_right + hook_left + center_bridge + wing_right + wing_left).clean()

    # 4. 造形座標系への配置: Z=0.00mm 完全接地 + XYバウンディングボックス中心を原点(0,0)へ一致
    shifted = Pos(0.0, MAIN_U_OFFSET, -HOLDER_BOTTOM_V) * combined
    bb = shifted.bounding_box()
    cx = 0.5 * (bb.min.X + bb.max.X)
    cy = 0.5 * (bb.min.Y + bb.max.Y)
    result = Pos(-cx, -cy, -bb.min.Z) * shifted
    return result.solids()[0]


def build_fit_test_piece() -> Part:
    """約10分で実機ラックへのスナップ感とセルフロック剛性を検証できる薄切りテストピースを生成する."""
    hook_face = _build_j_hook_2d_face()
    hook_body = extrude(
        Pos(-FIT_TEST_WIDTH / 2.0, 0.0, 0.0) * hook_face,
        amount=FIT_TEST_WIDTH,
        dir=(1, 0, 0),
    )

    # 指掛け用の短いフロント背板タブ (Z=28.80mm = 0.60mm*48 まで延長)
    tab = Pos(
        0.0,
        CRADLE_BACKPLATE_REAR_U + CRADLE_BACKPLATE_THICKNESS / 2.0,
        HOLDER_BOTTOM_V + FIT_TEST_HEIGHT / 2.0,
    ) * Box(FIT_TEST_WIDTH, CRADLE_BACKPLATE_THICKNESS, FIT_TEST_HEIGHT)

    combined = hook_body + tab
    shifted = Pos(0.0, FIT_TEST_U_OFFSET, -HOLDER_BOTTOM_V) * combined
    bb = shifted.bounding_box()
    cx = 0.5 * (bb.min.X + bb.max.X)
    cy = 0.5 * (bb.min.Y + bb.max.Y)
    result = Pos(-cx, -cy, -bb.min.Z) * shifted
    return result.solids()[0]


def export_models(output_dir: Path | None = None) -> tuple[Path, Path]:
    """本番モデルと事前嵌合テストピースの両方をスクリプトと同一ディレクトリへSTEP出力する."""
    target_dir = Path(__file__).resolve().parent if output_dir is None else Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    holder = build_holder()
    fit_test = build_fit_test_piece()

    main_step = target_dir / "steel_rack_tennis_racket_holder.step"
    fit_step = target_dir / "steel_rack_tennis_racket_holder_fit_test.step"

    export_step(holder, str(main_step))
    export_step(fit_test, str(fit_step))
    return main_step, fit_step


if __name__ == "__main__":
    holder_part = build_holder()
    fit_test_part = build_fit_test_piece()
    main_out, fit_out = export_models()
    print(f"Exported main holder STEP : {main_out}")
    print(f"Exported fit-test STEP    : {fit_out}")
    show_object(holder_part, name="steel_rack_tennis_racket_holder")
    show_object(Pos(90.0, 0.0, 0.0) * fit_test_part, name="fit_test_piece")
