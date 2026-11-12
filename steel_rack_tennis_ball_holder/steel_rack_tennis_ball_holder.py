"""
設計要件:
    - マットブラックのスチールラック（天板端部が下に18.1mm折り曲げられた約1.0mm厚の薄鉄板フチ ＋
      その板の垂直面から手前へ2.0mmクリアランスを空け、下端から2.0mm下に通る φ7.2mm 水平丸パイプ）に
      ガタつきゼロ・斜め抜けゼロでワンタッチ固定でき、硬式テニスボールを縦4段に独立収納できる
      皿型ボールスタンド（C字リング皿×縦4段・最上段レッドボール兼用・分割なし1ピース一体造形版）。
    - 構造的に最も高剛性かつ継手ガタが一切生じない「横桟から上方向へ立ち上がる1ピース一体造形タワー」を採用:
      1. 樹脂本体全高を 246.00mm（0.60mm × 410）とし、4球目上部を開放空間へ逃がすことで
         Bambu Lab P2S Combo の造形高さ上限（256mm）内に余裕をもって一体造形可能。
      2. 第1段C字リング皿の下部スカートを Z=0 ビルドプレートへ直接接地させるワイドU字フットプリントにより、
         ブリム不要で高層まで揺れゼロの安定造形を実現。
      3. 4球分の重心が丸パイプより手前に位置するため、重力モーメントが上部背面ストッパーを薄鉄板裏面へ
         押し付ける自己倍力ロック方向に働き、着脱時は第1段上の45°切妻アーチ窓から手前指先でリリースタブを引ける。
    - 取り出しやすい手前オープンC字リング皿 × 縦4段（74.40mmピッチ）:
      1. 手前45〜46mmのオープン開口（< 球径65.4mm）により振動や接触での自然落下を完全に防ぎつつ、
         上の皿に指が当たらず1〜4段すべて約9〜10mm持ち上げるだけで手前へサッと摘まみ出せる。
      2. 2〜4段目の下部支持部は、背面ラダースパインから45°でせり上がるサイドリブと直下ボール周囲の
         45°ティアドロップ円錐ドームくり抜きを組み合わせ、下段ボールとの干渉ゼロと完全サポートフリーを両立。
      3. 1〜3段目は通常硬式球（ITF規格 φ65.4〜68.6mm / 基準 φ67.0mm）専用テーパー座面、
         最上段（4段目）は内座で通常球を同軸保持しつつ外フレア座で大きめのレッドボール（φ75〜80mm）も
         安定保持できる連続2段凹面座とする。
    - 実機テスト検証済みの共通ロックモジュール `steel_rack_base_hook`（段付き丸パイプ専用ポケット幅7.70mm ＋
      頂点越えu=+4.55mm常時予圧35°ディープフック ＋ v=+9.60mm指掛けリリースタブ）をインポートして100%共有する。
    - モデルごとに専用ディレクトリで管理し、本番モデルと最上段2サイズ兼用座テストゲージの2つのSTEPファイルを同時出力する。

推奨フィラメント:
    - PETG（Bambu PETG HF / PETG Matte ブラック推奨 — 板バネラッチの長期耐クリープ性と高層積層強度の両立のため）
    - PLA Matte / PLA Tough でも使用可能（ボール4球の総重量は約230gと軽量であり、Z=0連続繊維リーフ設計によりPLAでも十分な強度を確保）。

推奨スライサー設定:
    - レイヤー高さ (Layer height): 0.20mm (0.4mmノズル時) または 0.30mm (0.6mmノズル時) — 全高246.00mm / 板バネ厚1.80mm すべて整数倍
    - 壁ループ (Wall loops): 3（246mm縦タワーおよびC字アームの剛性確保）
    - インフィル (Sparse infill): 15〜20% (Gyroid または Cross Hatch)
    - サポート (Supports): なし (None — 全オーバーハング55.0°以下・ブリッジゼロの完全サポートフリー設計)
    - ブリム (Brim): 不要（Z=0に横77mm×奥行93.3mmの広いU字接地面があるため安定）

印刷統計（予想）:
    - steel_rack_tennis_ball_holder.step: 印刷時間 約3時間50分〜4時間45分、フィラメント使用量 約180〜230g（ソリッド体積 359.94cm³）
    - steel_rack_tennis_ball_holder_fit_test.step: 印刷時間 約22〜28分、フィラメント使用量 約16〜20g（ソリッド体積 26.83cm³）

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

import math
from pathlib import Path
from build123d import *

from steel_rack_base_hook import (
    HOLDER_BOTTOM_V,
    HOOK_INNER_HALF_GAP,
    HOOK_REAR_BACK_U,
    J_DECK_TOP_V,
    J_FLOOR_TOP_V,
    J_FRONT_FUNNEL,
    J_FRONT_INNER_U,
    LATCH_ANCHOR_U,
    LATCH_LEAF_THICKNESS,
    LATCH_NOSE_BLUNT_H,
    LATCH_OVERHANG_DEG,
    LATCH_POCKET_GAP,
    LATCH_POCKET_REAR_U,
    LATCH_RELEASE_TOP_V,
    LATCH_SIDE_GAP,
    LATCH_STEM_BACK_U,
    LATCH_STEM_FRONT_U,
    LATCH_STEM_THICKNESS,
    LATCH_TIP_U,
    LATCH_TIP_V,
    LATCH_TOP_TAPER_U,
    LATCH_WIDTH,
    PIPE_CENTER_U,
    PIPE_CENTER_V,
    PIPE_CLEARANCE_FROM_SKIRT_U,
    PIPE_DIA,
    PIPE_GAP_TO_SKIRT_V,
    PIPE_RADIUS,
    PIPE_REAR_SEAT_U,
    PIPE_STEP_BOTTOM_V,
    SKIRT_HEIGHT,
    SKIRT_STEP_TOP_V,
    SKIRT_THICKNESS_MAX,
    STOPPER_FRONT_U,
    STOPPER_LEADIN_CHAMFER,
    STOPPER_TOP_V,
    build_steel_rack_mounting_core,
)

try:
    from ocp_vscode import show_object
except ImportError:  # pragma: no cover

    def show_object(*_args, **_kwargs) -> None:
        pass


# ==============================================================================
# 定数パラメーター定義 (単位: mm / 角度: deg)
# 内部設計座標:
#   x: ラック左右方向 (中央 x = 0.00)
#   u: 前後方向 (棚板の垂直面[前面] u = 0.00, 室内手前 +u, 棚奥側 -u)
#   v: ラック基準上下方向 (棚板前垂れ下端 v = 0.00, ビルドプレート接地 v = -15.00)
#   z: ビルドプレート基準高さ (z = v - HOLDER_BOTTOM_V = 0.00 〜 246.00mm)
#   ※ ラック実測値・段付きパイプ専用座・ディープフック板バネ定数は steel_rack_base_hook から共有
# ==============================================================================

NUM_BALL_TIERS = 4

# --- テニスボール基準直径 (ITF規格準拠) ---
STANDARD_BALL_DIA = 67.00  # 通常硬式テニスボール基準径 (ITF公差 65.41〜68.58mm)
RED_FELT_BALL_DIA = 75.00  # ステージ3 レッドボール (フェルト基準径 φ75mm)
RED_FOAM_BALL_DIA = 80.00  # ステージ3 レッドボール (スポンジ基準径 φ80mm)

# --- 造形全体高さ設定 (0.20mm / 0.30mm レイヤー両対応の 0.60mm 整数倍) ---
TOWER_TOTAL_HEIGHT = 246.00  # 本番モデル全高 (0.60mm * 410 <= Bambu P2S 上限 256.0mm)
HOLDER_TOP_V = HOLDER_BOTTOM_V + TOWER_TOTAL_HEIGHT  # +231.00mm
MOUNT_CORE_TOP_Z = 28.80  # 下部マウントコアおよび第1窓下端高さ (v = +13.80mm)

# --- デュアル剛体Jフック外幅 ---
HOOK_OUTER_HALF_SPAN = 34.00  # 全幅 68.00mm のワイド剛体デュアルJフック

# --- ラダーフレーム縦スパイン ＆ 45°切妻アーチ窓寸法 ---
SPINE_REAR_U = LATCH_POCKET_REAR_U  # +21.90mm
SPINE_THICKNESS = 6.60  # 高層246mmを支える縦柱前後厚
SPINE_FRONT_U = SPINE_REAR_U + SPINE_THICKNESS  # +28.50mm
WINDOW_HALF_WIDTH = 13.00  # 中央アーチ窓の片側幅 (開口26.00mm / 左右柱各21.00mm幅)

# --- 4段C字リング皿 ＆ 2サイズ兼用座面パラメーター ---
U_BALL_CENTER = 65.00  # ボール中心前後座標 (スパイン前面+28.50mmから36.50mm前方)

# #1〜#3段: 通常硬式球 (φ67.0mm) 専用3-4-5テーパー座面 (dz/dr = 4/3)
TIER_1_SEAT_BOT_Z = 12.60  # 第1段座面下端 (0.60mm * 21)
TIER_PITCH_Z = 74.40  # 1〜3段の上下ピッチ (0.60mm * 124)
STD_RING_HEIGHT = 6.00  # リング座面高さ (0.60mm * 10 -> 上端 18.60, 93.00, 167.40mm)
STD_SEAT_R_BOT = 25.30  # 座面下端内半径 (φ50.60mm)
STD_SEAT_R_TOP = 29.80  # 座面上端内半径 (φ59.60mm -> dz/dr = 6.00/4.50 = 4/3)
STD_RING_OUTER_R = 38.50  # #1〜#3段の外半径 (横幅 77.00mm)
STD_FRONT_GAP_HALF_X = 22.50  # 手前オープン開口の片側幅 (開口 45.00mm < 球径 65.4mm)
STD_ARM_TIP_U = 89.50  # #1〜#3段のC字アーム手前端座標

# #4段 (最上段): 通常球(φ67mm) ＆ レッドボール(φ75〜80mm) 兼用の連続2段凹面座
TOP_STAGE_A_BOT_Z = 235.80  # 内座下端 (0.60mm * 393)
TOP_STAGE_A_TOP_Z = 240.40  # 内座→外フレア遷移高さ
TOP_RING_TOP_Z = TOWER_TOTAL_HEIGHT  # 246.00mm (0.60mm * 410)
TOP_SEAT_R_BOT = 24.80  # 下段内座の下端半径 (φ49.60mm)
TOP_SEAT_R_MID = 28.80  # 遷移半径 (dz/dr_A = 4.60/4.00 = 1.15 -> φ67球が r=25.28mm で接線着座)
TOP_SEAT_R_TOP = 33.47  # 上端半径 (dz/dr_B = 5.60/4.67 = 1.20 > 1.15 -> φ75/φ80球が接線着座)
TOP_RING_OUTER_R = 41.50  # 最上段の外半径 (横幅 83.00mm)
TOP_FRONT_GAP_HALF_X = 22.50  # 最上段の手前開口片側幅 (開口 45.00mm — レッドボールもしっかり前抱え保持)
TOP_ARM_TIP_U = 94.50  # 最上段のC字アーム手前端座標

FIT_TEST_HEIGHT = TOP_RING_TOP_Z - TOP_STAGE_A_BOT_Z  # 10.20mm (= 0.60mm * 17 の2サイズ座面テストゲージ)

# 下段ボール非干渉 ＆ 45°完全サポートフリーくり抜きドーム半径・シェル肉厚
BALL_CLEARANCE_DOME_R = 38.50  # 下段基準球(R=33.5mm)に対して全方向 +5.0mm 以上の余裕を確保
DISH_SHELL_WALL_THICKNESS = 7.50  # 下部45°リブの均一構造シェル肉厚
ARM_TIP_VERTICAL_THICKNESS = 4.80  # C字アーム先端の最小垂直厚み

# 全体奥行センタリングオフセット (最前端 TOP_ARM_TIP_U = +94.50mm と 背面 HOOK_REAR_BACK_U = -6.80mm の中心)
MAIN_U_OFFSET = -(HOOK_REAR_BACK_U + TOP_ARM_TIP_U) / 2.0  # -43.85mm


def _cone_tangent_ball_center_z(
    ball_radius: float,
    z_bot: float,
    r_bot: float,
    z_top: float,
    r_top: float,
) -> float:
    """円錐台座面 (r_bot, z_bot) -> (r_top, z_top) に球体 R が接線着座する球中心 Z 座標を返す."""
    m = (r_top - r_bot) / (z_top - z_bot)  # dr / dz
    r_tan = ball_radius / math.sqrt(1.0 + m * m)
    r_clamped = min(max(r_tan, r_bot), r_top)
    z_contact = z_bot + (r_clamped - r_bot) / m
    return z_contact + math.sqrt(max(0.0, ball_radius * ball_radius - r_clamped * r_clamped))


def compute_ball_center_z(tier_idx: int, ball_radius: float = STANDARD_BALL_DIA / 2.0) -> float:
    """指定段 (0..3) に半径 ball_radius のボールを置いた際の理論着座中心 Z 座標を返す."""
    if not 0 <= tier_idx < NUM_BALL_TIERS:
        raise ValueError(f"tier_idx must be in 0..{NUM_BALL_TIERS - 1}, got {tier_idx}")

    if tier_idx < NUM_BALL_TIERS - 1:
        z_bot = TIER_1_SEAT_BOT_Z + tier_idx * TIER_PITCH_Z
        z_top = z_bot + STD_RING_HEIGHT
        return _cone_tangent_ball_center_z(ball_radius, z_bot, STD_SEAT_R_BOT, z_top, STD_SEAT_R_TOP)

    # 最上段 (#4): 2段連続凹面座のうちより高い位置で支持する段が実着座高さとなる
    z_stage_a = _cone_tangent_ball_center_z(
        ball_radius,
        TOP_STAGE_A_BOT_Z,
        TOP_SEAT_R_BOT,
        TOP_STAGE_A_TOP_Z,
        TOP_SEAT_R_MID,
    )
    z_stage_b = _cone_tangent_ball_center_z(
        ball_radius,
        TOP_STAGE_A_TOP_Z,
        TOP_SEAT_R_MID,
        TOP_RING_TOP_Z,
        TOP_SEAT_R_TOP,
    )
    return max(z_stage_a, z_stage_b)


def _build_teardrop_clearance_dome(z_ball_center: float) -> Part:
    """直下ボール周囲 +5.0mm を確保しつつ上面を 45.0° 円錐で閉じた完全サポートフリーくり抜きドーム."""
    r_dome = BALL_CLEARANCE_DOME_R
    r_tan = r_dome * math.sin(math.radians(45.0))
    z_tan_rel = r_dome * math.cos(math.radians(45.0))
    z_apex_rel = z_tan_rel + r_tan
    z_cyl_bot_rel = -36.0

    # XZ平面 (r >= 0, z) で右半分プロファイルを作成し Z軸まわりに360°回転
    with BuildSketch(Plane.XZ) as sk_dome:
        with BuildLine():
            Polyline(
                (0.0, z_cyl_bot_rel),
                (r_dome, z_cyl_bot_rel),
                (r_dome, 0.0),
            )
            RadiusArc((r_dome, 0.0), (r_tan, z_tan_rel), -r_dome)
            Polyline(
                (r_tan, z_tan_rel),
                (0.0, z_apex_rel),
                (0.0, z_cyl_bot_rel),
            )
        make_face()
    dome = revolve(sk_dome.sketch, axis=Axis.Z, revolution_arc=360.0)
    return Pos(0.0, U_BALL_CENTER, z_ball_center) * dome


def _build_c_ring_outer_footprint_2d(
    outer_r: float,
    gap_half_x: float,
    arm_tip_u: float,
) -> Sketch:
    """スパイン背面から手前オープンC字アーム先端まで滑らかに繋がる2D外形スケッチ (Plane.XY) を返す."""
    with BuildSketch(Plane.XY) as sk:
        # 1. 円形リング外形 + スパイン接続台形ベース
        with Locations((0.0, U_BALL_CENTER)):
            Circle(outer_r)
        with BuildLine():
            Polyline(
                (-HOOK_OUTER_HALF_SPAN, SPINE_REAR_U),
                (HOOK_OUTER_HALF_SPAN, SPINE_REAR_U),
                (outer_r, U_BALL_CENTER),
                (-outer_r, U_BALL_CENTER),
                (-HOOK_OUTER_HALF_SPAN, SPINE_REAR_U),
            )
        make_face()

        # 2. アーム手前端 (u > arm_tip_u) のフラットカット
        front_clip_len = 40.0
        with Locations((0.0, arm_tip_u + 0.5 * front_clip_len)):
            Rectangle(2.0 * outer_r + 20.0, front_clip_len, mode=Mode.SUBTRACT)

        # 3. 手前オープンC字開口 (|x| < gap_half_x, u >= U_BALL_CENTER)
        gap_len = arm_tip_u - U_BALL_CENTER + 10.0
        with Locations((0.0, U_BALL_CENTER + 0.5 * gap_len)):
            Rectangle(2.0 * gap_half_x, gap_len, mode=Mode.SUBTRACT)

        # 4. 指が触れるC字アーム手前先端の角に R2.00mm の滑らかな保護Rを付与
        tip_vertices = [vtx for vtx in sk.vertices() if vtx.Y > arm_tip_u - 1.0]
        if tip_vertices:
            fillet(tip_vertices, 2.00)

    return sk.sketch


def _build_revolved_seat_cutter(
    z_bot_hole: float,
    profile_rz: list[tuple[float, float]],
    outer_r_for_shell: float | None = None,
) -> Part:
    """ボール着座テーパー面・下部45°中空シェル・中央貫通穴を同時に彫り込む回転体カッターを返す."""
    r_first, z_first = profile_rz[0]
    r_last, z_last = profile_rz[-1]

    lower_pts: list[tuple[float, float]] = [(0.0, z_bot_hole)]
    if outer_r_for_shell is not None:
        r_shell_in = outer_r_for_shell - DISH_SHELL_WALL_THICKNESS
        if r_shell_in > r_first + 0.5:
            z_flare_bot = z_first - (r_shell_in - r_first)  # 厳密 45.0° 内面フレア (サポート不要)
            if z_flare_bot > z_bot_hole + 0.5:
                lower_pts.extend([(r_shell_in, z_bot_hole), (r_shell_in, z_flare_bot)])
            else:
                r_at_bot = r_first + (z_first - z_bot_hole)
                lower_pts.append((r_at_bot, z_bot_hole))
        else:
            lower_pts.append((r_first, z_bot_hole))
    else:
        lower_pts.append((r_first, z_bot_hole))

    pts = lower_pts + profile_rz + [(r_last, z_last + 2.0), (0.0, z_last + 2.0), (0.0, z_bot_hole)]
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine():
            Polyline(*pts)
        make_face()
    cutter = revolve(sk.sketch, axis=Axis.Z, revolution_arc=360.0)
    return Pos(0.0, U_BALL_CENTER, 0.0) * cutter


def _build_dish_tier(tier_idx: int) -> Part:
    """指定段 (0..3) の完全サポートフリーC字リング皿ソリッドを生成する."""
    is_top = tier_idx == NUM_BALL_TIERS - 1
    if not is_top:
        z_seat_bot = TIER_1_SEAT_BOT_Z + tier_idx * TIER_PITCH_Z
        z_ring_top = z_seat_bot + STD_RING_HEIGHT
        outer_r = STD_RING_OUTER_R
        gap_half_x = STD_FRONT_GAP_HALF_X
        arm_tip_u = STD_ARM_TIP_U
        seat_profile = [
            (STD_SEAT_R_BOT, z_seat_bot),
            (STD_SEAT_R_TOP, z_ring_top),
        ]
    else:
        z_seat_bot = TOP_STAGE_A_BOT_Z
        z_ring_top = TOP_RING_TOP_Z
        outer_r = TOP_RING_OUTER_R
        gap_half_x = TOP_FRONT_GAP_HALF_X
        arm_tip_u = TOP_ARM_TIP_U
        seat_profile = [
            (TOP_SEAT_R_BOT, TOP_STAGE_A_BOT_Z),
            (TOP_SEAT_R_MID, TOP_STAGE_A_TOP_Z),
            (TOP_SEAT_R_TOP, TOP_RING_TOP_Z),
        ]

    footprint = _build_c_ring_outer_footprint_2d(outer_r, gap_half_x, arm_tip_u)

    if tier_idx == 0:
        # 第1段 (#1): Z=0 ビルドプレートへ直接接地させてワイドU字安定ベースを形成
        blank = extrude(footprint, amount=z_ring_top)
        seat_cutter = _build_revolved_seat_cutter(z_bot_hole=-2.0, profile_rz=seat_profile)
        return blank - seat_cutter

    # 第2〜4段 (#2〜#4): 背面スパインから45.0°でせり上がる下部傾斜面 ＋ 直下ボール45°ティアドロップくり抜き
    z_tip_underside = z_ring_top - ARM_TIP_VERTICAL_THICKNESS
    u_span_from_spine = arm_tip_u - SPINE_FRONT_U
    z_root_at_spine = z_tip_underside - u_span_from_spine  # 厳密 45.0° 傾斜 (dz/du = +1.00)

    z_extrude_bot = max(0.0, z_root_at_spine - 8.0)
    blank = Pos(0.0, 0.0, z_extrude_bot) * extrude(footprint, amount=z_ring_top - z_extrude_bot)

    # 1. スパイン前面 (u = SPINE_FRONT_U) からアーム先端へ向かう 45.0° 下部ウェッジカット
    u_cut_max = arm_tip_u + 15.0
    z_at_u_cut_max = z_root_at_spine + (u_cut_max - SPINE_FRONT_U)
    wedge_pts = [
        (SPINE_FRONT_U, z_extrude_bot - 2.0),
        (u_cut_max, z_extrude_bot - 2.0),
        (u_cut_max, z_at_u_cut_max),
        (SPINE_FRONT_U, z_root_at_spine),
        (SPINE_FRONT_U, z_extrude_bot - 2.0),
    ]
    with BuildSketch(Plane.YZ.offset(- outer_r - 10.0)) as sk_wedge:
        with BuildLine():
            Polyline(*wedge_pts)
        make_face()
    wedge_cut = extrude(sk_wedge.sketch, amount=2.0 * (outer_r + 10.0))

    # 2. 直下ボールの着座中心を基準とする 45° ティアドロップ・クリアランスドームの減算
    z_prev_ball = compute_ball_center_z(tier_idx - 1, STANDARD_BALL_DIA / 2.0)
    dome_cut = _build_teardrop_clearance_dome(z_prev_ball)

    # 3. 当該段のボール着座テーパー座面＆下部45°軽量化中空シェルカット
    seat_cutter = _build_revolved_seat_cutter(
        z_bot_hole=z_extrude_bot - 2.0,
        profile_rz=seat_profile,
        outer_r_for_shell=outer_r,
    )

    return blank - wedge_cut - dome_cut - seat_cutter


def _build_gable_window_cutter(z_sill: float, z_apex: float) -> Part:
    """幅 2*WINDOW_HALF_WIDTH・屋根傾斜 45.0° の切妻アーチ窓カッターを生成する."""
    z_eave = z_apex - WINDOW_HALF_WIDTH
    with BuildSketch(Plane.XZ.offset(-SPINE_REAR_U + 4.0)) as sk_win:
        with BuildLine():
            Polyline(
                (-WINDOW_HALF_WIDTH, z_sill),
                (WINDOW_HALF_WIDTH, z_sill),
                (WINDOW_HALF_WIDTH, z_eave),
                (0.0, z_apex),
                (-WINDOW_HALF_WIDTH, z_eave),
                (-WINDOW_HALF_WIDTH, z_sill),
            )
        make_face()
    # Plane.XZ の法線は -Y なので amount=-28.0 で +Y 方向 (u = 17.9 〜 45.9mm) へ貫通押し出し
    return extrude(sk_win.sketch, amount=-28.0)


def _build_ladder_spine() -> Part:
    """左右21mm幅の剛体縦柱2本と各段横梁からなるラダーフレーム縦スパイン (z=0..246mm) を生成する."""
    spine_h = TOWER_TOTAL_HEIGHT - MOUNT_CORE_TOP_Z
    spine_box = Pos(
        0.0,
        0.5 * (SPINE_REAR_U + SPINE_FRONT_U),
        MOUNT_CORE_TOP_Z + 0.5 * spine_h,
    ) * Box(2.0 * HOOK_OUTER_HALF_SPAN, SPINE_THICKNESS, spine_h)
    return spine_box


def build_holder() -> Part:
    """4段C字リング皿 ＋ 最上段レッドボール兼用座 ＋ v4高保持ロック搭載の1ピース本番モデルを生成する."""
    mounting_core = build_steel_rack_mounting_core(
        outer_half_span=HOOK_OUTER_HALF_SPAN,
        spine_thickness=SPINE_THICKNESS,
        spine_height=MOUNT_CORE_TOP_Z,
        add_front_notch=False,
        align_bottom_to_z0=True,
    )
    part = mounting_core + _build_ladder_spine()
    for idx in range(NUM_BALL_TIERS):
        part = part + _build_dish_tier(idx)

    # 第1段上の指入れリリース窓 ＋ 第2・第3段上の軽量化45°切妻トラス窓を貫通カット
    windows = [
        (MOUNT_CORE_TOP_Z, 73.00),
        (98.40, 147.00),
        (173.40, 222.00),
    ]
    for z_sill, z_apex in windows:
        part = part - _build_gable_window_cutter(z_sill, z_apex)

    cleaned = part.clean()
    shifted = Pos(0.0, MAIN_U_OFFSET, 0.0) * cleaned
    bb = shifted.bounding_box()
    cx = 0.5 * (bb.min.X + bb.max.X)
    cy = 0.5 * (bb.min.Y + bb.max.Y)
    result = Pos(-cx, -cy, -bb.min.Z) * shifted
    return result.solids()[0]


def build_fit_test_piece() -> Part:
    """最上段(#4)の通常球(φ67mm)＆レッドボール(φ75〜80mm)連続2段凹面座と手前46mm開口を確認する薄型リングゲージ."""
    footprint = _build_c_ring_outer_footprint_2d(
        TOP_RING_OUTER_R,
        TOP_FRONT_GAP_HALF_X,
        TOP_ARM_TIP_U,
    )
    blank = extrude(footprint, amount=FIT_TEST_HEIGHT)
    seat_profile = [
        (TOP_SEAT_R_BOT, 0.0),
        (TOP_SEAT_R_MID, TOP_STAGE_A_TOP_Z - TOP_STAGE_A_BOT_Z),
        (TOP_SEAT_R_TOP, FIT_TEST_HEIGHT),
    ]
    seat_cutter = _build_revolved_seat_cutter(z_bot_hole=-1.0, profile_rz=seat_profile)
    gauge = (blank - seat_cutter).clean()

    bb = gauge.bounding_box()
    cx = 0.5 * (bb.min.X + bb.max.X)
    cy = 0.5 * (bb.min.Y + bb.max.Y)
    result = Pos(-cx, -cy, -bb.min.Z) * gauge
    return result.solids()[0]


def export_models(output_dir: Path | None = None) -> tuple[Path, Path]:
    """本番4段ボールスタンドと2サイズ座面テストゲージをスクリプトと同一ディレクトリへSTEP出力する."""
    target_dir = Path(__file__).resolve().parent if output_dir is None else Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    holder = build_holder()
    fit_test = build_fit_test_piece()

    main_step = target_dir / "steel_rack_tennis_ball_holder.step"
    fit_step = target_dir / "steel_rack_tennis_ball_holder_fit_test.step"

    export_step(holder, str(main_step))
    export_step(fit_test, str(fit_step))
    return main_step, fit_step


if __name__ == "__main__":
    holder_part = build_holder()
    fit_test_part = build_fit_test_piece()
    main_out, fit_out = export_models()
    print(f"Exported main ball holder STEP : {main_out}")
    print(f"Exported fit-test gauge STEP   : {fit_out}")
    show_object(holder_part, name="steel_rack_tennis_ball_holder")
    show_object(Pos(105.0, 0.0, 0.0) * fit_test_part, name="dual_size_ring_gauge")
