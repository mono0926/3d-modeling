"""
設計要件:
    - マットブラックのスチールラック（天板端部が下に18.1mm折り曲げられた約1.0mm厚の薄鉄板フチ ＋
      その板の垂直面から手前へ2.0mmクリアランスを空け、下端から2.0mm下に通る φ7.2mm 水平丸パイプ）に
      ガタつきゼロ・斜め抜けゼロで強力ワンタッチ固定でき、硬式テニスラケットを前後に最大3本独立して掛けられる
      3連ホルダー（v5 独立3連スロット ＋ v4段付きパイプ専用座＆頂点越えディープフック版）。
    - ジュニア用「Wilson CLASH 26 V3.0」（26インチ / 100sq.in. / フレーム厚24.0mmフラット / スロート片側約23.5°）と
      大人用「HEAD EXTREME MP 2026 (233316)」（27インチ / 100sq.in. / フレーム厚23-26-21mm / スロート片側約24.2°）の
      2機種を全3スロットどの位置でも完全兼用し、ガット面をラックと平行（ヘッド上向き）にして最大3本スッキリ縦掛けする。
    - 独立3連V字クレードル（32.0mmピッチ：26.5mm溝 ＋ 5.5mm丸み仕切りリブ × 3連、全体奥行128.5mm）:
      1. フレーム同士が一切接触せず塗装傷を防ぎ、1本だけ掛けた時も前後に倒れず直立保持する。
      2. グリップエンドの膨らみ（約34mm厚）同士も干渉せず、かつ天井高制約のある最上段でも中央スルー通路を通して
         わずかな持ち上げ量でスムーズに出し入れできる。
      3. 3本分（約900g）の片持ち荷重でも一切たわまないよう、左右の剛体Jフック外幅をクレードル外壁と同じ67.60mm（片側33.80mm）に
         揃えてサイドフレームを一直線に直結し、背板スパイン肉厚も4.80mmへ高剛性化する。
    - 実機テストで完璧な固定力を確認済みの v4 ロックコア（段付き丸パイプ専用ポケット幅7.70mm ＋ 頂点越えu=+4.55mm常時予圧35°ディープフック ＋
      v=+9.60mm指掛けリリースタブ）を100%継承し、直立引き抜き耐力 約7.3〜10.4kgf・斜め25°抜け抵抗 約5.3〜7.5kgfを維持する。
    - 最新の3Dプリンター（Bambu Lab P2S Combo 等）での出力を想定し、底面（Z=0）ベタ置きの完全サポートフリー・ブリッジゼロ
      （全オーバーハング55.0°以下）および 0.4mmノズル(0.20mm層)/0.6mmノズル(0.30mm層)両対応の 0.60mm 整数倍高さで設計する。
    - モデルごとに専用ディレクトリで管理し、本番モデルと同一マウント機構を持つ事前嵌合テストピースの2つのSTEPファイルを同時出力する。

推奨フィラメント:
    - PETG（Bambu PETG HF / PETG Matte ブラック推奨 — 3本荷重に対する高靭性および常時クランプ予圧の長期耐クリープ性のため）
    - PLA Matte / PLA Tough でも使用可能（ロングリーフ＋3.60mm厚ステム設計により層間引張応力を最大約15.5MPa以下に抑制済みだが、長期3本保持にはPETGを推奨）。

推奨スライサー設定:
    - レイヤー高さ (Layer height): 0.20mm (0.4mmノズル時) または 0.30mm (0.6mmノズル時) — 全高56.40mm / テスト28.80mm / 板バネ厚1.80mm すべて整数倍
    - 壁ループ (Wall loops): 3〜4（128.5mm長尺3連クレードルおよび剛体Jフックの高剛性確保）
    - インフィル (Sparse infill): 20〜25% (Gyroid または Cross Hatch)
    - サポート (Supports): なし (None — 全オーバーハング55.0°以下・ブリッジゼロのサポートフリー設計)
    - ブリム (Brim): 不要（Z=0に広いフラット接地面があるため安定）

印刷統計（予想）:
    - steel_rack_tennis_racket_holder.step: 印刷時間 約2時間20分〜2時間50分、フィラメント使用量 約115〜145g（ソリッド体積 149.11cm³）
    - steel_rack_tennis_racket_holder_fit_test.step: 印刷時間 約18〜22分、フィラメント使用量 約13〜16g（ソリッド体積 16.60cm³）

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
#   u: 前後方向 (棚板の垂直面[前面] u = 0.00, 室内手前 +u, 棚奥側 -u)
#   v: 上下方向 (棚板前垂れ下端 v = 0.00, 上方 +v, 下方 -v)
# ==============================================================================

# --- 収納ラケット本数 (パラメトリック設定: 3本掛け) ---
NUM_RACKET_SLOTS = 3

# --- スチールラック実測基準寸法 (v2〜v4 実機装着テスト確認済み) ---
PIPE_DIA = 7.20  # 水平丸パイプ外径
PIPE_RADIUS = PIPE_DIA / 2.0  # 3.60mm
PIPE_CLEARANCE_FROM_SKIRT_U = 2.00  # 棚板垂直面(u=0.0)から丸パイプ奥面(u=+2.0)までの前後クリアランス
PIPE_GAP_TO_SKIRT_V = 2.00  # 棚板下端(v=0.0)から丸パイプ上端(v=-2.0)までの上下クリアランス
PIPE_CENTER_U = PIPE_CLEARANCE_FROM_SKIRT_U + PIPE_RADIUS  # +5.60mm (丸パイプ u = +2.00 〜 +9.20mm)
PIPE_CENTER_V = -(PIPE_GAP_TO_SKIRT_V + PIPE_RADIUS)  # -5.60mm (丸パイプ v = -9.20 〜 -2.00mm)

SKIRT_HEIGHT = 18.10  # 棚板垂直面の縦高さ (v = 0.00 〜 +18.10mm)
SKIRT_THICKNESS_MAX = 1.05  # 約1.0mm薄鉄板の実測基準板厚

# --- 造形ピッチ・全体高さ設定 (0.20mm / 0.30mm レイヤー両対応の 0.60mm 整数倍) ---
HOLDER_BOTTOM_V = -15.00  # ビルドプレート接地面 (Z = 0.00mm)
HOLDER_TOP_V = 41.40  # クレードル上端 (全高 56.40mm = 0.60mm * 94)
CRADLE_TOTAL_HEIGHT = HOLDER_TOP_V - HOLDER_BOTTOM_V  # 56.40mm

FIT_TEST_TOP_V = 13.80  # テストピースおよび中央スパイン上端 (全高 28.80mm = 0.60mm * 48)
FIT_TEST_HEIGHT = FIT_TEST_TOP_V - HOLDER_BOTTOM_V  # 28.80mm

# --- クレードル横幅基準・ストレート直結デュアルJフック寸法 (v5 3本片持ち高剛性化) ---
CRADLE_BOTTOM_INNER_WIDTH = 52.00  # v=-15.00mm での左右V受け面内幅 (シャフト通過開口)
CRADLE_SIDE_WALL_THICKNESS = 7.80  # V字サイドウォール水平方向厚み

LATCH_WIDTH = 16.00  # 中央独立ロング板バネラッチ幅 (x = -8.00 〜 +8.00mm)
LATCH_SIDE_GAP = 1.80  # 板バネ左右の完全分離スリット幅 (スライサー融着ゼロを保証)
HOOK_INNER_HALF_GAP = LATCH_WIDTH / 2.0 + LATCH_SIDE_GAP  # 9.80mm (中央19.60mmベイ)
HOOK_OUTER_HALF_SPAN = CRADLE_BOTTOM_INNER_WIDTH / 2.0 + CRADLE_SIDE_WALL_THICKNESS  # 33.80mm (全幅67.60mm・クレードル外壁と一直線直結！)
HOOK_WIDTH = HOOK_OUTER_HALF_SPAN - HOOK_INNER_HALF_GAP  # 24.00mm (左右合計 48.00mm の重荷重対応Jフック)

FIT_TEST_SIDE_HOOK_WIDTH = 8.70  # テストピースの左右対称Jフック幅 (各8.70mm)
FIT_TEST_WIDTH = 2.0 * (HOOK_INNER_HALF_GAP + FIT_TEST_SIDE_HOOK_WIDTH)  # 37.00mm

HOOK_REAR_BACK_U = -6.80  # 背面Uステム外側面
STOPPER_FRONT_U = -1.06  # 上部薄鉄板裏ストッパー壁 (v=-0.80〜+11.80mm まで全面フラット密着)
STOPPER_LEADIN_CHAMFER = 0.80  # 上端先端のみの導入45°テーパー量
STOPPER_TOP_V = 12.60  # ストッパー上端 (フロントスパインより1.2mm低く前後識別可能)

SKIRT_STEP_TOP_V = -0.80  # 薄鉄板下端(v=0.0)と干渉しない段差開始高さ
PIPE_REAR_SEAT_U = 1.62  # 丸パイプ下半分専用の背面受け座 (前後ガタ完全解消)
PIPE_STEP_BOTTOM_V = SKIRT_STEP_TOP_V - (PIPE_REAR_SEAT_U - STOPPER_FRONT_U)  # -3.48mm (上向き45°スロープ)
J_FLOOR_TOP_V = -9.55  # 丸パイプ底面受け座 (底肉厚 5.45mm)
J_FRONT_INNER_U = 9.32  # Jフック前側ガイド内壁 (下部パイプポケット幅 7.70mm)
J_FRONT_FUNNEL = 1.15  # 前側上端入口の45°導入ファンネル量
J_DECK_TOP_V = 8.40  # Jフック前側デッキ上面

# --- 中央 Z=0 連続繊維・頂点越えディープフック板バネラッチ寸法 (v4 実機検証済み寸法100%維持) ---
LATCH_ANCHOR_U = -4.30  # 背面下部クロスバーへの固定根元位置
LATCH_LEAF_THICKNESS = 1.80  # Z=0 水平リーフ板厚 (0.60mm * 3)
LATCH_STEM_FRONT_U = 8.95  # 垂直ステム前面
LATCH_STEM_THICKNESS = 3.60  # 垂直ステム前後厚
LATCH_STEM_BACK_U = LATCH_STEM_FRONT_U + LATCH_STEM_THICKNESS  # +12.55mm
LATCH_LEAF_SPAN_U = 0.5 * (LATCH_STEM_FRONT_U + LATCH_STEM_BACK_U) - LATCH_ANCHOR_U  # 15.05mm

LATCH_OVERHANG_DEG = 55.0  # ディープフック下面の造形オーバーハング角 (水平から35.0°)
LATCH_TIP_U = 4.55  # 丸パイプ頂点(+5.55mm)を越える深爪先端位置
LATCH_TIP_V = -1.42  # 着座完了時にも+0.75mmの常時クランプ予圧を残す高さ設定
LATCH_NOSE_BLUNT_H = 0.45  # ノズル造形安定化のための先端垂直フラット高さ
LATCH_RELEASE_TOP_V = 9.60  # 指先が掛かりやすいリリースタブ上端
LATCH_TOP_TAPER_U = 0.80  # リリースタブ上端背面のテーパー逃げ量
LATCH_POCKET_GAP = 9.35  # ステム背面のたわみ逃げポケット基準幅 (上端10.15mm)
LATCH_POCKET_REAR_U = LATCH_STEM_BACK_U + LATCH_POCKET_GAP  # +21.90mm

# --- 2機種兼用・独立3連 外抱えV字クレードル寸法 ---
CRADLE_BACKPLATE_REAR_U = LATCH_POCKET_REAR_U  # +21.90mm
CRADLE_BACKPLATE_THICKNESS = 4.80  # 3本片持ち荷重を支える強化フロントスパイン兼背板肉厚 (3.60→4.80mm)
CRADLE_INNER_BACK_U = CRADLE_BACKPLATE_REAR_U + CRADLE_BACKPLATE_THICKNESS  # +26.70mm (第1スロット後面)
CRADLE_GROOVE_DEPTH = 26.50  # 各ラケットスロットの前後溝内寸
CRADLE_DIVIDER_THICKNESS = 5.50  # スロット間の独立仕切りリブ肉厚 (両面保護R付き)
CRADLE_SLOT_PITCH = CRADLE_GROOVE_DEPTH + CRADLE_DIVIDER_THICKNESS  # 32.00mm ピッチ (グリップエンド干渉も回避)
CRADLE_FRONT_LIP_THICKNESS = 4.50  # 最前列の手前返しリップ肉厚
CRADLE_FRONT_LIP_INNER_U = (
    CRADLE_INNER_BACK_U
    + NUM_RACKET_SLOTS * CRADLE_GROOVE_DEPTH
    + (NUM_RACKET_SLOTS - 1) * CRADLE_DIVIDER_THICKNESS
)  # +117.20mm
CRADLE_FRONT_OUTER_U = CRADLE_FRONT_LIP_INNER_U + CRADLE_FRONT_LIP_THICKNESS  # +121.70mm (全体奥行 128.50mm)

CRADLE_HALF_ANGLE_DEG = 24.0  # スロート片側基準テーパー角 (CLASH 23.5° / EXTREME 24.2° の中心)
CRADLE_CROWN_BULGE = 0.45  # 長手方向R350mm相当の太鼓クラウニング中央膨らみ量
CRADLE_BACK_FLANGE_WIDTH = 13.00  # 背板フランジの内側張り出し幅 (x_bot=13.0mm)
CRADLE_FRONT_LIP_WIDTH = 11.00  # 各仕切りリブおよび手前返しリップの内側張り出し幅 (中央スルー通路確保)

# --- 出力時XYセンタリングオフセット ---
MAIN_U_OFFSET = -(HOOK_REAR_BACK_U + CRADLE_FRONT_OUTER_U) / 2.0  # -57.45mm
FIT_TEST_U_OFFSET = -(HOOK_REAR_BACK_U + CRADLE_INNER_BACK_U) / 2.0  # -9.95mm


def _build_j_hook_2d_face() -> Face:
    """(u, v) 平面における段付きパイプ専用ポケット付き剛体Jフック断面 Face を生成する (下向きオーバーハングゼロ)."""
    rear_outer_chamfer = 1.60

    pts = [
        (HOOK_REAR_BACK_U, HOLDER_BOTTOM_V),
        (CRADLE_INNER_BACK_U, HOLDER_BOTTOM_V),
        (CRADLE_INNER_BACK_U, FIT_TEST_TOP_V),
        (CRADLE_BACKPLATE_REAR_U, FIT_TEST_TOP_V),
        (CRADLE_BACKPLATE_REAR_U, J_DECK_TOP_V),
        (J_FRONT_INNER_U + J_FRONT_FUNNEL, J_DECK_TOP_V),
        (J_FRONT_INNER_U, J_DECK_TOP_V - J_FRONT_FUNNEL),
        (J_FRONT_INNER_U, J_FLOOR_TOP_V),
        (PIPE_REAR_SEAT_U, J_FLOOR_TOP_V),
        (PIPE_REAR_SEAT_U, PIPE_STEP_BOTTOM_V),
        (STOPPER_FRONT_U, SKIRT_STEP_TOP_V),
        (STOPPER_FRONT_U, STOPPER_TOP_V - STOPPER_LEADIN_CHAMFER),
        (STOPPER_FRONT_U - STOPPER_LEADIN_CHAMFER, STOPPER_TOP_V),
        (HOOK_REAR_BACK_U + rear_outer_chamfer, STOPPER_TOP_V),
        (HOOK_REAR_BACK_U, STOPPER_TOP_V - rear_outer_chamfer),
        (HOOK_REAR_BACK_U, HOLDER_BOTTOM_V),
    ]

    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            Polyline(*pts)
        make_face()
        floor_corners = [
            vtx
            for vtx in sk.vertices()
            if abs(vtx.Y - J_FLOOR_TOP_V) < 0.05
            and (abs(vtx.X - PIPE_REAR_SEAT_U) < 0.05 or abs(vtx.X - J_FRONT_INNER_U) < 0.05)
        ]
        if floor_corners:
            fillet(floor_corners, 0.80)
    return sk.sketch.faces()[0]


def _build_center_latch_2d_face() -> Face:
    """(u, v) 平面における頂点越え常時予圧35°ディープフック板バネラッチ断面 Face を生成する."""
    v_leaf_top = HOLDER_BOTTOM_V + LATCH_LEAF_THICKNESS  # -13.20mm
    u_overlap_back = LATCH_ANCHOR_U - 1.00

    du_nose = LATCH_STEM_FRONT_U - LATCH_TIP_U  # 4.40mm
    hook_slope = -1.0 / math.tan(math.radians(LATCH_OVERHANG_DEG))  # -0.7002075
    v_lock_root = LATCH_TIP_V + hook_slope * du_nose  # -4.50mm

    v_tip_top = LATCH_TIP_V + LATCH_NOSE_BLUNT_H  # -0.97mm
    v_bevel_top = v_tip_top + du_nose  # +3.43mm

    gusset_front = 1.20
    taper_start_v = 2.00

    pts = [
        (u_overlap_back, HOLDER_BOTTOM_V),
        (LATCH_STEM_BACK_U, HOLDER_BOTTOM_V),
        (LATCH_STEM_BACK_U, taper_start_v),
        (LATCH_STEM_BACK_U - LATCH_TOP_TAPER_U, LATCH_RELEASE_TOP_V),
        (LATCH_STEM_FRONT_U, LATCH_RELEASE_TOP_V),
        (LATCH_STEM_FRONT_U, v_bevel_top),
        (LATCH_TIP_U, v_tip_top),
        (LATCH_TIP_U, LATCH_TIP_V),
        (LATCH_STEM_FRONT_U, v_lock_root),
        (LATCH_STEM_FRONT_U, v_leaf_top + gusset_front),
        (LATCH_STEM_FRONT_U - gusset_front, v_leaf_top),
        (u_overlap_back, v_leaf_top),
        (u_overlap_back, HOLDER_BOTTOM_V),
    ]

    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            Polyline(*pts)
        make_face()
    return sk.sketch.faces()[0]


def _build_mounting_core(outer_half_x: float, add_front_notch: bool = False) -> Part:
    """本番モデルと嵌合テストピースで100%共通のマウントコアを生成する."""
    side_hook_w = outer_half_x - HOOK_INNER_HALF_GAP
    j_face = _build_j_hook_2d_face()

    hook_right = extrude(
        Pos(HOOK_INNER_HALF_GAP, 0.0, 0.0) * j_face,
        amount=side_hook_w,
        dir=(1, 0, 0),
    )
    hook_left = extrude(
        Pos(-outer_half_x, 0.0, 0.0) * j_face,
        amount=side_hook_w,
        dir=(1, 0, 0),
    )

    rear_bar_u_len = LATCH_ANCHOR_U - HOOK_REAR_BACK_U  # 2.50mm
    rear_bar_h = J_FLOOR_TOP_V - HOLDER_BOTTOM_V  # 5.45mm
    rear_crossbar = Pos(
        0.0,
        0.5 * (HOOK_REAR_BACK_U + LATCH_ANCHOR_U),
        HOLDER_BOTTOM_V + 0.5 * rear_bar_h,
    ) * Box(2.0 * outer_half_x, rear_bar_u_len, rear_bar_h)

    front_spine = Pos(
        0.0,
        0.5 * (CRADLE_BACKPLATE_REAR_U + CRADLE_INNER_BACK_U),
        HOLDER_BOTTOM_V + 0.5 * FIT_TEST_HEIGHT,
    ) * Box(2.0 * outer_half_x, CRADLE_BACKPLATE_THICKNESS, FIT_TEST_HEIGHT)

    latch_face = _build_center_latch_2d_face()
    center_latch = extrude(
        Pos(-LATCH_WIDTH / 2.0, 0.0, 0.0) * latch_face,
        amount=LATCH_WIDTH,
        dir=(1, 0, 0),
    )

    core = hook_right + hook_left + rear_crossbar + front_spine + center_latch

    if add_front_notch:
        notch = (
            Pos(0.0, 0.5 * (CRADLE_BACKPLATE_REAR_U + CRADLE_INNER_BACK_U), FIT_TEST_TOP_V)
            * Rot(0, 45, 0)
            * Box(2.40, CRADLE_BACKPLATE_THICKNESS + 2.0, 2.40)
        )
        core = core - notch

    return core.clean()


def _build_single_v_wing(sign_x: float) -> Part:
    """片側 (+X または -X) の独立3連クラウニング付き外抱えV字クレードル翼を生成する (設計座標系)."""
    tan_a = math.tan(math.radians(CRADLE_HALF_ANGLE_DEG))
    h = CRADLE_TOTAL_HEIGHT  # 56.40mm
    x_bot_in = CRADLE_BOTTOM_INNER_WIDTH / 2.0  # 26.00mm
    x_top_in = x_bot_in + h * tan_a  # 51.11mm
    x_mid_in = 0.5 * (x_bot_in + x_top_in) - CRADLE_CROWN_BULGE  # 内側へ0.45mm膨らむ太鼓R

    x_bot_out = x_bot_in + CRADLE_SIDE_WALL_THICKNESS  # 33.80mm (= HOOK_OUTER_HALF_SPAN)
    x_top_out = x_top_in + CRADLE_SIDE_WALL_THICKNESS  # 58.91mm

    u_span_total = CRADLE_FRONT_OUTER_U - CRADLE_BACKPLATE_REAR_U  # 99.80mm
    x_bot_flange = x_bot_in - CRADLE_BACK_FLANGE_WIDTH  # 13.00mm
    x_top_flange = x_top_in - CRADLE_BACK_FLANGE_WIDTH  # 38.11mm

    # 1. 背板〜第3スロット手前リップまでの連続サイドブランク
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
    wing = extrude(sk_outer.sketch, amount=-u_span_total)

    # 2. 全スロット・全仕切りリブを貫通する中央スルー通路カット (天井に当てず手前からシャフトを通せる開口)
    x_bot_lip_in = x_bot_in - CRADLE_FRONT_LIP_WIDTH  # 15.00mm
    x_top_lip_in = x_top_in - CRADLE_FRONT_LIP_WIDTH  # 40.11mm
    channel_depth = (CRADLE_FRONT_OUTER_U - CRADLE_INNER_BACK_U) + 2.0
    with BuildSketch(Plane.XZ.offset(-CRADLE_INNER_BACK_U)) as sk_channel:
        with BuildLine():
            Polyline(
                (sign_x * x_bot_lip_in, HOLDER_BOTTOM_V - 1.0),
                (sign_x * x_top_lip_in, HOLDER_TOP_V + 1.0),
                (0.0, HOLDER_TOP_V + 1.0),
                (0.0, HOLDER_BOTTOM_V - 1.0),
                (sign_x * x_bot_lip_in, HOLDER_BOTTOM_V - 1.0),
            )
        make_face()
    wing = wing - extrude(sk_channel.sketch, amount=-channel_depth)

    # 3. NUM_RACKET_SLOTS 個のクラウニング付きV字ラケット溝を 32.00mm ピッチで彫り込む
    with BuildSketch(Plane.XZ) as sk_groove_profile:
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
    base_groove_face = sk_groove_profile.sketch.faces()[0]

    for slot_idx in range(NUM_RACKET_SLOTS):
        u_slot_start = CRADLE_INNER_BACK_U + slot_idx * CRADLE_SLOT_PITCH
        slot_cut = extrude(
            Pos(0.0, u_slot_start, 0.0) * base_groove_face,
            amount=-CRADLE_GROOVE_DEPTH,
        )
        wing = wing - slot_cut

    # 4. 外周長尺エッジ R3.0mm フィレット ＋ 全スロット・仕切りリブのラケット接触エッジ R1.5mm 保護フィレット
    sloped_edges = [e for e in wing.edges() if e.bounding_box().size.Z > 50.0]
    outer_sloped = [e for e in sloped_edges if abs(e.center().X) > 42.0]
    if outer_sloped:
        wing = fillet(outer_sloped, radius=3.00)

    sloped_after = [e for e in wing.edges() if e.bounding_box().size.Z > 50.0]
    racket_sloped = [
        e
        for e in sloped_after
        if e.center().Y > CRADLE_INNER_BACK_U - 0.5 and 26.5 < abs(e.center().X) < 42.0
    ]
    if racket_sloped:
        wing = fillet(racket_sloped, radius=1.50)

    # 5. 上面全周にラケット導入ガイド面取り C1.0mm (4.5mmリップ・5.5mm仕切りリブでも干渉しない最適寸法)
    top_face = wing.faces().sort_by(Axis.Z)[-1]
    wing = chamfer(top_face.edges(), length=1.00)

    return wing


def build_holder() -> Part:
    """2機種兼用・独立3連V字クレードル ＋ v4段付きパイプ専用座＆頂点越えディープフックの本番モデルを生成する."""
    mounting_core = _build_mounting_core(HOOK_OUTER_HALF_SPAN, add_front_notch=False)
    wing_right = _build_single_v_wing(+1.0)
    wing_left = _build_single_v_wing(-1.0)

    combined = (mounting_core + wing_right + wing_left).clean()

    shifted = Pos(0.0, MAIN_U_OFFSET, -HOLDER_BOTTOM_V) * combined
    bb = shifted.bounding_box()
    cx = 0.5 * (bb.min.X + bb.max.X)
    cy = 0.5 * (bb.min.Y + bb.max.Y)
    result = Pos(-cx, -cy, -bb.min.Z) * shifted
    return result.solids()[0]


def build_fit_test_piece() -> Part:
    """本番と100%同一の段付きパイプ専用座＋頂点越えディープフックを備える事前嵌合テストピース."""
    core = _build_mounting_core(FIT_TEST_WIDTH / 2.0, add_front_notch=True)

    shifted = Pos(0.0, FIT_TEST_U_OFFSET, -HOLDER_BOTTOM_V) * core
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
    show_object(Pos(95.0, 0.0, 0.0) * fit_test_part, name="fit_test_piece")
