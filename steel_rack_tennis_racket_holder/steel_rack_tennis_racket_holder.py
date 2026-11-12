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
    - 実機テストで完璧な固定力を確認済みの共通ロックモジュール `steel_rack_base_hook`（段付き丸パイプ専用ポケット幅7.70mm ＋
      頂点越えu=+4.55mm常時予圧35°ディープフック ＋ v=+9.60mm指掛けリリースタブ）をインポートして100%共有し、
      直立引き抜き耐力 約7.3〜10.4kgf・斜め25°抜け抵抗 約5.3〜7.5kgfを維持する。
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

from steel_rack_base_hook import (
    FIT_TEST_HEIGHT,
    FIT_TEST_SIDE_HOOK_WIDTH,
    FIT_TEST_TOP_V,
    FIT_TEST_WIDTH,
    HOLDER_BOTTOM_V,
    HOOK_INNER_HALF_GAP,
    HOOK_REAR_BACK_U,
    J_DECK_TOP_V,
    J_FLOOR_TOP_V,
    J_FRONT_FUNNEL,
    J_FRONT_INNER_U,
    LATCH_ANCHOR_U,
    LATCH_LEAF_SPAN_U,
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
    build_steel_rack_fit_test_piece,
    build_steel_rack_mounting_core,
)

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
#   ※ ラック実測値・段付きパイプ専用座・ディープフック板バネ定数は steel_rack_base_hook から共有
# ==============================================================================

# --- 収納ラケット本数 (パラメトリック設定: 3本掛け) ---
NUM_RACKET_SLOTS = 3

# --- クレードル全体高さ設定 (0.20mm / 0.30mm レイヤー両対応の 0.60mm 整数倍) ---
HOLDER_TOP_V = 41.40  # クレードル上端 (全高 56.40mm = 0.60mm * 94)
CRADLE_TOTAL_HEIGHT = HOLDER_TOP_V - HOLDER_BOTTOM_V  # 56.40mm

# --- クレードル横幅基準・ストレート直結デュアルJフック外幅 (v5 3本片持ち高剛性化) ---
CRADLE_BOTTOM_INNER_WIDTH = 52.00  # v=-15.00mm での左右V受け面内幅 (シャフト通過開口)
CRADLE_SIDE_WALL_THICKNESS = 7.80  # V字サイドウォール水平方向厚み
HOOK_OUTER_HALF_SPAN = CRADLE_BOTTOM_INNER_WIDTH / 2.0 + CRADLE_SIDE_WALL_THICKNESS  # 33.80mm (全幅67.60mm・クレードル外壁と一直線直結！)
HOOK_WIDTH = HOOK_OUTER_HALF_SPAN - HOOK_INNER_HALF_GAP  # 24.00mm (左右合計 48.00mm の重荷重対応Jフック)

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
    mounting_core = build_steel_rack_mounting_core(
        outer_half_span=HOOK_OUTER_HALF_SPAN,
        spine_thickness=CRADLE_BACKPLATE_THICKNESS,
        spine_height=FIT_TEST_HEIGHT,
        add_front_notch=False,
        align_bottom_to_z0=False,
    )
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
    return build_steel_rack_fit_test_piece(spine_thickness=CRADLE_BACKPLATE_THICKNESS)


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
