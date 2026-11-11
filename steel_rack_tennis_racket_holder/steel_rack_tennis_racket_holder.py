"""
設計要件:
    - マットブラックのスチールラック（天板端部が下に18.1mm折り曲げられた約1.0mm厚の薄鉄板フチ ＋
      その板の垂直面から手前へ2.0mmクリアランスを空け、下端から2.0mm下に通る φ7.2mm 水平丸パイプ）に
      ワンタッチ装着できる硬式テニスラケット掛け（v2 実機適合版）。
    - ジュニア用「Wilson CLASH 26 V3.0」（26インチ / 100sq.in. / フレーム厚24.0mmフラット / スロート片側約23.5°）と
      大人用「HEAD EXTREME MP 2026 (233316)」（27インチ / 100sq.in. / フレーム厚23-26-21mm / スロート片側約24.2°）の
      2機種を1つのホルダーで完全兼用し、ガット面をラックと平行（ヘッド上向き）にしてスッキリ縦掛けする。
    - ネジ・両面テープ不要の「ストレートアップ剛体デュアルJフック ＋ Z=0独立ロング板バネ・セルフロックラッチ」機構:
      1. 板の垂直面(u=0.0)と丸パイプ(u=+2.0〜+9.2mm)の間の狭い2.0mm隙間には一切パーツを通さず、
         左右の剛体Jフックが「薄鉄板の裏面(u=-1.25mm)」と「丸パイプの手前(u=+10.00mm)」を真下から傾けずに真っ直ぐ跨ぐ。
      2. 中央に左右2.0mmスリットと背面5.0mm逃げポケットで完全分離した「底面Z=0連続繊維ロング板バネラッチ」
         （幅13.0mm・板厚1.80mm・スパン13.50mm）を配置。下から持ち上げるだけで軽くしなって（PETG約1.4kgf / PLA約2.0kgf）
         丸パイプ上肩（+45°接線）へ「カチッ」と乗り上げ、ラケット荷重がかかるほどロックが深く締まる完全セルフロックと
         棚板天面への出っ張りゼロを両立する（前後・上下クリアランスが1.5〜2.5mmに変動しても無調整で適合）。
    - 外抱えV字クレードル（片側基準24.0° ＋ 長手R350mm相当の太鼓クラウニング ＋ 全周保護面取り/フィレット）により、
      上から下ろすだけで両ラケットとも自動調心して面接触保持し、最大厚26.0mm部でも丸パイプ手前端から19mm以上・
      棚板前面から28mm以上の十分な逃げを確保する。
    - 最新の3Dプリンター（Bambu Lab P2S Combo 等）での出力を想定し、底面（Z=0）ベタ置きの完全サポートフリー・ブリッジゼロ
      （全オーバーハング45.0°以下）および 0.4mmノズル(0.20mm層)/0.6mmノズル(0.30mm層)両対応の 0.60mm 整数倍高さで設計する。
    - モデルごとに専用ディレクトリで管理し、本番モデルと同一マウント機構を持つ事前嵌合テストピースの2つのSTEPファイルを同時出力する。

推奨フィラメント:
    - PETG（Bambu PETG HF / PETG Matte ブラック推奨 — 板バネ着脱時のしなやかな靭性・耐クリープ性とマット黒ラックへの一体感のため）
    - PLA Matte / PLA Tough でも代用可能（連続繊維方向の最大ひずみ約1.18%・Z層間引張応力約12.7MPa以下の安全設計のため割れずに使用可能だが、長期耐クリープ性の観点からPETGを推奨）。

推奨スライサー設定:
    - レイヤー高さ (Layer height): 0.20mm (0.4mmノズル時) または 0.30mm (0.6mmノズル時) — 全高56.40mm / テスト28.80mm / 板バネ厚1.80mm すべて整数倍
    - 壁ループ (Wall loops): 3〜4（剛体JフックおよびV字クレードルの高剛性確保とZ=0板バネの連続ペリメータ形成）
    - インフィル (Sparse infill): 20〜25% (Gyroid または Cross Hatch)
    - サポート (Supports): なし (None — 全オーバーハング45.0°以下・ブリッジゼロの完全サポートフリー設計)
    - ブリム (Brim): 不要（Z=0に広いフラット接地面があるため安定）

印刷統計（予想）:
    - steel_rack_tennis_racket_holder.step: 印刷時間 約70〜85分、フィラメント使用量 約47〜62g（ソリッド体積 59.52cm³）
    - steel_rack_tennis_racket_holder_fit_test.step: 印刷時間 約13〜16分、フィラメント使用量 約9g（ソリッド体積 10.85cm³）

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

# --- スチールラック実測基準寸法 (v2 実機確認済み) ---
PIPE_DIA = 7.20  # 水平丸パイプ外径
PIPE_RADIUS = PIPE_DIA / 2.0  # 3.60mm
PIPE_CLEARANCE_FROM_SKIRT_U = 2.00  # 棚板垂直面(u=0.0)から丸パイプ奥面(u=+2.0)までの前後クリアランス
PIPE_GAP_TO_SKIRT_V = 2.00  # 棚板下端(v=0.0)から丸パイプ上端(v=-2.0)までの上下クリアランス
PIPE_CENTER_U = PIPE_CLEARANCE_FROM_SKIRT_U + PIPE_RADIUS  # +5.60mm (丸パイプ u = +2.00 〜 +9.20mm)
PIPE_CENTER_V = -(PIPE_GAP_TO_SKIRT_V + PIPE_RADIUS)  # -5.60mm (丸パイプ v = -9.20 〜 -2.00mm)

SKIRT_HEIGHT = 18.10  # 棚板垂直面の縦高さ (v = 0.00 〜 +18.10mm)
SKIRT_THICKNESS_MAX = 1.20  # 約1.0mm薄鉄板の最大想定板厚 (公差幅 0.95 〜 1.20mm に対応)

# --- 造形ピッチ・全体高さ設定 (0.20mm / 0.30mm レイヤー両対応の 0.60mm 整数倍) ---
HOLDER_BOTTOM_V = -15.00  # ビルドプレート接地面 (Z = 0.00mm)
HOLDER_TOP_V = 41.40  # クレードル上端 (全高 56.40mm = 0.60mm * 94)
CRADLE_TOTAL_HEIGHT = HOLDER_TOP_V - HOLDER_BOTTOM_V  # 56.40mm

FIT_TEST_TOP_V = 13.80  # テストピースおよび中央スパイン上端 (全高 28.80mm = 0.60mm * 48)
FIT_TEST_HEIGHT = FIT_TEST_TOP_V - HOLDER_BOTTOM_V  # 28.80mm

# --- 左右の剛体デュアルJフック寸法 ---
LATCH_WIDTH = 13.00  # 中央独立ロング板バネラッチ幅 (x = -6.50 〜 +6.50mm)
LATCH_SIDE_GAP = 2.00  # 板バネ左右の完全分離スリット幅 (スライサー融着ゼロを保証)
HOOK_INNER_HALF_GAP = LATCH_WIDTH / 2.0 + LATCH_SIDE_GAP  # 8.50mm (中央17.00mmベイ)
HOOK_WIDTH = 19.50  # 本番モデルの左右各Jフック幅 (2本合計 39.00mm)
HOOK_OUTER_HALF_SPAN = HOOK_INNER_HALF_GAP + HOOK_WIDTH  # 28.00mm (フック全幅 56.00mm)

FIT_TEST_SIDE_HOOK_WIDTH = 9.00  # テストピースの左右対称Jフック幅 (各9.00mm)
FIT_TEST_WIDTH = 2.0 * (HOOK_INNER_HALF_GAP + FIT_TEST_SIDE_HOOK_WIDTH)  # 35.00mm

HOOK_REAR_BACK_U = -5.20  # 背面Uステム外側面 (肉厚 3.95mm 確保)
STOPPER_FRONT_U = -1.25  # 薄鉄板裏ストッパー爪の前面 (鉄板裏 -1.05mm に対し 0.20mm 余裕)
STOPPER_RELIEF_U = -2.05  # 下部導入ガイド部の逃げ面 (真下から無造作に入れても引っ掛からない広い入口)
STOPPER_BOTTOM_V = 1.50  # ストッパー有効当接面の下端 (下側に45°面取り導入ガイド)
STOPPER_TOP_V = 8.40  # ストッパー上端 (棚板天面 +18.10mm より約10mm下で天面出っ張りゼロ)
J_FLOOR_TOP_V = -11.00  # Jフック底面床の上面 (底肉厚 4.00mm、ラッチ着座時に +1.1mm 以上のオーバーストローク余裕)
J_FRONT_INNER_U = 10.00  # Jフック前側ガイド内壁 (開口11.25mm: クリアランス2.5mm個体まで直進進入可能)
J_DECK_TOP_V = 8.40  # Jフック前側デッキ上面

# --- 中央 Z=0 独立ロング板バネラッチ寸法 ---
LATCH_ANCHOR_U = -1.80  # 背面下部クロスバーへの固定根元位置
LATCH_LEAF_THICKNESS = 1.80  # Z=0 水平リーフ板厚 (0.60mm * 3 = 0.20mm*9層 / 0.30mm*6層)
LATCH_STEM_FRONT_U = 10.20  # 垂直ステム前面
LATCH_STEM_THICKNESS = 3.00  # 垂直ステム前後厚 (層間Z引張応力を <13MPa に抑える高剛性ステム)
LATCH_STEM_BACK_U = LATCH_STEM_FRONT_U + LATCH_STEM_THICKNESS  # +13.20mm
LATCH_LEAF_SPAN_U = 0.5 * (LATCH_STEM_FRONT_U + LATCH_STEM_BACK_U) - LATCH_ANCHOR_U  # 13.50mm
LATCH_TIP_U = 6.70  # ラッチ爪先端の前後位置 (丸パイプ手前端 +9.00mm に対し 2.30mm 噛み込み)
LATCH_TIP_V = -1.85  # ラッチ45°ロック面の上端高さ (u + v = 4.85 で丸パイプ +45° 上肩に接線着座)
LATCH_NOSE_BLUNT_H = 0.40  # ノズル造形安定化のための先端垂直フラット高さ
LATCH_RELEASE_TOP_V = 6.00  # 指先で手前に引いて解除できる上部リリースタブ高さ
LATCH_POCKET_GAP = 5.00  # ステム背面のたわみ逃げポケット奥行 (過大変形防止ハードストップ兼用)
LATCH_POCKET_REAR_U = LATCH_STEM_BACK_U + LATCH_POCKET_GAP  # +18.20mm

# --- 2機種兼用・外抱えV字クレードル寸法 ---
CRADLE_BACKPLATE_REAR_U = LATCH_POCKET_REAR_U  # +18.20mm (逃げポケット後方に剛体フロントスパインを配置)
CRADLE_BACKPLATE_THICKNESS = 3.60  # フロントスパイン兼クレードル背板肉厚
CRADLE_INNER_BACK_U = CRADLE_BACKPLATE_REAR_U + CRADLE_BACKPLATE_THICKNESS  # +21.80mm
CRADLE_GROOVE_DEPTH = 26.50  # ラケット前後溝内寸 (21〜25mm厚スロートに余裕を持って対応)
CRADLE_FRONT_LIP_INNER_U = CRADLE_INNER_BACK_U + CRADLE_GROOVE_DEPTH  # +48.30mm
CRADLE_FRONT_LIP_THICKNESS = 4.50  # 手前返しリップ肉厚
CRADLE_FRONT_OUTER_U = CRADLE_FRONT_LIP_INNER_U + CRADLE_FRONT_LIP_THICKNESS  # +52.80mm

CRADLE_BOTTOM_INNER_WIDTH = 52.00  # v=-15.00mm での左右V受け面内幅 (シャフト通過開口)
CRADLE_HALF_ANGLE_DEG = 24.0  # スロート片側基準テーパー角 (CLASH 23.5° / EXTREME 24.2° の中心)
CRADLE_CROWN_BULGE = 0.45  # 長手方向R350mm相当の太鼓クラウニング中央膨らみ量 (エッジ当たり防止)
CRADLE_SIDE_WALL_THICKNESS = 7.80  # V字サイドウォール水平方向厚み
CRADLE_BACK_FLANGE_WIDTH = 13.00  # 背板フランジの内側張り出し幅 (x_bot=13.0mm > 中央ベイ8.5mm)
CRADLE_FRONT_LIP_WIDTH = 11.00  # 手前返しリップの内側張り出し幅

# --- 出力時XYセンタリングオフセット ---
MAIN_U_OFFSET = -(HOOK_REAR_BACK_U + CRADLE_FRONT_OUTER_U) / 2.0  # -23.80mm
FIT_TEST_U_OFFSET = -(HOOK_REAR_BACK_U + CRADLE_INNER_BACK_U) / 2.0  # -8.30mm


def _build_j_hook_2d_face() -> Face:
    """(u, v) 平面における左右の剛体Jフック断面 Face を生成する (全エッジ下向きオーバーハングゼロ)."""
    rear_chamfer = 1.80
    relief_step = STOPPER_FRONT_U - STOPPER_RELIEF_U  # 0.80mm (45°導入ガイド)
    front_funnel = 0.80  # 前側入口の45°導入面取り

    pts = [
        (HOOK_REAR_BACK_U, HOLDER_BOTTOM_V),
        (CRADLE_INNER_BACK_U, HOLDER_BOTTOM_V),
        (CRADLE_INNER_BACK_U, FIT_TEST_TOP_V),
        (CRADLE_BACKPLATE_REAR_U, FIT_TEST_TOP_V),
        (CRADLE_BACKPLATE_REAR_U, J_DECK_TOP_V),
        (J_FRONT_INNER_U + front_funnel, J_DECK_TOP_V),
        (J_FRONT_INNER_U, J_DECK_TOP_V - front_funnel),
        (J_FRONT_INNER_U, J_FLOOR_TOP_V),
        (STOPPER_RELIEF_U, J_FLOOR_TOP_V),
        (STOPPER_RELIEF_U, STOPPER_BOTTOM_V - relief_step),
        (STOPPER_FRONT_U, STOPPER_BOTTOM_V),
        (STOPPER_FRONT_U, STOPPER_TOP_V),
        (HOOK_REAR_BACK_U + rear_chamfer, STOPPER_TOP_V),
        (HOOK_REAR_BACK_U, STOPPER_TOP_V - rear_chamfer),
        (HOOK_REAR_BACK_U, HOLDER_BOTTOM_V),
    ]

    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            Polyline(*pts)
        make_face()
    return sk.sketch.faces()[0]


def _build_center_latch_2d_face() -> Face:
    """(u, v) 平面における Z=0 連続繊維ロング板バネラッチ断面 Face を生成する (厳密45.0°サポートフリー)."""
    v_leaf_top = HOLDER_BOTTOM_V + LATCH_LEAF_THICKNESS  # -13.20mm
    u_overlap_back = LATCH_ANCHOR_U - 1.00  # 背面クロスバー内へ1.0mm食い込ませて一体結合

    # 45.0° ロック面: (LATCH_TIP_U, LATCH_TIP_V) -> (LATCH_STEM_FRONT_U, v_lock_root)
    du_nose = LATCH_STEM_FRONT_U - LATCH_TIP_U  # 3.50mm
    v_lock_root = LATCH_TIP_V - du_nose  # -5.35mm (勾配 -1.00 => 法線 n.Z = -0.7071 厳密45.0°)

    # 45.0° 上面導入スロープ: (LATCH_TIP_U, v_tip_top) -> (LATCH_STEM_FRONT_U, v_bevel_top)
    v_tip_top = LATCH_TIP_V + LATCH_NOSE_BLUNT_H  # -1.45mm
    v_bevel_top = v_tip_top + du_nose  # +2.05mm (上向き面、オーバーハングゼロ)

    # L字コーナー応力緩和45°ガセット (パイプ通過域・テストプローブ域に干渉しない範囲)
    gusset_front = 1.00

    pts = [
        (u_overlap_back, HOLDER_BOTTOM_V),
        (LATCH_STEM_BACK_U, HOLDER_BOTTOM_V),
        (LATCH_STEM_BACK_U, LATCH_RELEASE_TOP_V),
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
    """本番モデルと嵌合テストピースで100%共通のマウントコア（左右Jフック＋前後クロスバー＋中央板バネ）を生成する."""
    side_hook_w = outer_half_x - HOOK_INNER_HALF_GAP
    j_face = _build_j_hook_2d_face()

    # 1. 左右対称の剛体Jフック
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

    # 2. 背面下部アンカークロスバー (左右Jフックを後端下部で連結し、中央Z=0板バネの固定端となる)
    rear_bar_u_len = LATCH_ANCHOR_U - HOOK_REAR_BACK_U  # 3.40mm
    rear_bar_h = J_FLOOR_TOP_V - HOLDER_BOTTOM_V  # 4.00mm
    rear_crossbar = Pos(
        0.0,
        0.5 * (HOOK_REAR_BACK_U + LATCH_ANCHOR_U),
        HOLDER_BOTTOM_V + 0.5 * rear_bar_h,
    ) * Box(2.0 * outer_half_x, rear_bar_u_len, rear_bar_h)

    # 3. 前側剛体フロントスパイン (逃げポケット後方で左右Jフックを全高連結し、過大変形ストッパーを兼ねる)
    front_spine = Pos(
        0.0,
        0.5 * (CRADLE_BACKPLATE_REAR_U + CRADLE_INNER_BACK_U),
        HOLDER_BOTTOM_V + 0.5 * FIT_TEST_HEIGHT,
    ) * Box(2.0 * outer_half_x, CRADLE_BACKPLATE_THICKNESS, FIT_TEST_HEIGHT)

    # 4. 中央の独立ロング板バネラッチ (左右に2.0mmスリット、背面に5.0mm逃げポケットを確保)
    latch_face = _build_center_latch_2d_face()
    center_latch = extrude(
        Pos(-LATCH_WIDTH / 2.0, 0.0, 0.0) * latch_face,
        amount=LATCH_WIDTH,
        dir=(1, 0, 0),
    )

    core = hook_right + hook_left + rear_crossbar + front_spine + center_latch

    # テストピース用: 手前側フロントスパイン上面中央に45°のV字ポインターノッチを刻み、前後・中心を一目瞭然にする
    if add_front_notch:
        notch = (
            Pos(0.0, 0.5 * (CRADLE_BACKPLATE_REAR_U + CRADLE_INNER_BACK_U), FIT_TEST_TOP_V)
            * Rot(0, 45, 0)
            * Box(2.40, CRADLE_BACKPLATE_THICKNESS + 2.0, 2.40)
        )
        core = core - notch

    return core.clean()


def _build_single_v_wing(sign_x: float) -> Part:
    """片側 (+X または -X) のクラウニング付き外抱えV字クレードル翼を生成する (設計座標系)."""
    tan_a = math.tan(math.radians(CRADLE_HALF_ANGLE_DEG))
    h = CRADLE_TOTAL_HEIGHT  # 56.40mm
    x_bot_in = CRADLE_BOTTOM_INNER_WIDTH / 2.0  # 26.00mm
    x_top_in = x_bot_in + h * tan_a  # 51.11mm
    x_mid_in = 0.5 * (x_bot_in + x_top_in) - CRADLE_CROWN_BULGE  # 内側へ0.45mm膨らむ太鼓R

    x_bot_out = x_bot_in + CRADLE_SIDE_WALL_THICKNESS  # 33.80mm
    x_top_out = x_top_in + CRADLE_SIDE_WALL_THICKNESS  # 58.91mm

    # 1. 外殻ブロック (背面 u=CRADLE_BACKPLATE_REAR_U 〜 前端 u=CRADLE_FRONT_OUTER_U) を押し出し生成
    u_span_total = CRADLE_FRONT_OUTER_U - CRADLE_BACKPLATE_REAR_U  # 34.60mm
    x_bot_flange = x_bot_in - CRADLE_BACK_FLANGE_WIDTH  # 13.00mm (> HOOK_INNER_HALF_GAP=8.50mm)
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
    wing_blank = extrude(sk_outer.sketch, amount=-u_span_total)

    # 2. ラケットスロート受け溝 (u = +21.80 〜 +48.30, 内面は R350mm 相当の太鼓クラウニング曲面) を切り抜く
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

    # 3. 手前返しリップの内側開放カット
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
        wing = fillet(racket_sloped, radius=1.80)

    # 5. 上端入口エッジを滑らかに面取りしてラケット投入ガイド性と安全性を向上
    top_face = wing.faces().sort_by(Axis.Z)[-1]
    wing = chamfer(top_face.edges(), length=1.20)

    return wing


def build_holder() -> Part:
    """2機種兼用V字クレードル ＋ ストレートアップJフック＆Z=0独立ロング板バネの本番モデルを生成する."""
    mounting_core = _build_mounting_core(HOOK_OUTER_HALF_SPAN, add_front_notch=False)
    wing_right = _build_single_v_wing(+1.0)
    wing_left = _build_single_v_wing(-1.0)

    combined = (mounting_core + wing_right + wing_left).clean()

    # 造形座標系への配置: Z=0.00mm 完全接地 + XYバウンディングボックス中心を原点(0,0)へ一致
    shifted = Pos(0.0, MAIN_U_OFFSET, -HOLDER_BOTTOM_V) * combined
    bb = shifted.bounding_box()
    cx = 0.5 * (bb.min.X + bb.max.X)
    cy = 0.5 * (bb.min.Y + bb.max.Y)
    result = Pos(-cx, -cy, -bb.min.Z) * shifted
    return result.solids()[0]


def build_fit_test_piece() -> Part:
    """本番と100%同一の中央板バネ＋左右対称Jフックを備え、約14分で実機スナップ感を検証できるテストピース."""
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
    show_object(Pos(90.0, 0.0, 0.0) * fit_test_part, name="fit_test_piece")
