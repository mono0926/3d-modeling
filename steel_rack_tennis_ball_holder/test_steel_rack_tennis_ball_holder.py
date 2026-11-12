"""スチールラック用テニスボールスタンド (steel_rack_tennis_ball_holder) の自動幾何・物理検証テスト."""

import math
import tempfile
import unittest
from pathlib import Path
from build123d import Box, Cylinder, Sphere, Pos, Rot, import_step

from steel_rack_tennis_ball_holder.steel_rack_tennis_ball_holder import (
    FIT_TEST_HEIGHT,
    HOLDER_BOTTOM_V,
    HOLDER_TOP_V,
    HOOK_INNER_HALF_GAP,
    HOOK_OUTER_HALF_SPAN,
    LATCH_OVERHANG_DEG,
    LATCH_POCKET_GAP,
    LATCH_STEM_BACK_U,
    LATCH_TIP_U,
    LATCH_TIP_V,
    MAIN_U_OFFSET,
    NUM_BALL_TIERS,
    PIPE_CENTER_U,
    PIPE_CENTER_V,
    PIPE_DIA,
    PIPE_RADIUS,
    RED_FELT_BALL_DIA,
    RED_FOAM_BALL_DIA,
    SKIRT_HEIGHT,
    SPINE_FRONT_U,
    SPINE_REAR_U,
    STANDARD_BALL_DIA,
    TOWER_TOTAL_HEIGHT,
    U_BALL_CENTER,
    build_fit_test_piece,
    build_holder,
    compute_ball_center_z,
    export_models,
)


def _intersect_volume(part_a, part_b) -> float:
    """build123d で非交差時に None が返る仕様を吸収して交差体積 (mm³) を返す."""
    common = part_a & part_b
    if common is None:
        return 0.0
    return sum(s.volume for s in common.solids())


class TestSteelRackTennisBallHolder(unittest.TestCase):
    """4段C字リング皿ボールスタンドの単一多様体・ラック嵌合・球体着座/保持/取出・造形性を検証する."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.holder = build_holder()
        cls.fit_test = build_fit_test_piece()

    def test_01_single_manifold_solid_and_p2s_build_volume(self) -> None:
        """本番モデルとテストゲージが単一多様体であり、Z=0接地・XY中央配置・P2S上限256mm以内を満たすこと."""
        self.assertEqual(NUM_BALL_TIERS, 4)
        self.assertTrue(self.holder.is_valid)
        self.assertEqual(len(self.holder.solids()), 1)
        self.assertTrue(self.fit_test.is_valid)
        self.assertEqual(len(self.fit_test.solids()), 1)

        bb = self.holder.bounding_box()
        self.assertAlmostEqual(bb.min.Z, 0.0, places=2)
        self.assertAlmostEqual(bb.size.Z, TOWER_TOTAL_HEIGHT, places=2)
        self.assertAlmostEqual(TOWER_TOTAL_HEIGHT, 246.00, places=2)
        self.assertLessEqual(bb.size.Z, 256.0)
        self.assertLessEqual(bb.size.X, 256.0)
        self.assertLessEqual(bb.size.Y, 256.0)
        self.assertAlmostEqual(0.5 * (bb.min.X + bb.max.X), 0.0, places=2)
        self.assertAlmostEqual(0.5 * (bb.min.Y + bb.max.Y), 0.0, places=2)

        # 0.20mm / 0.30mm 両レイヤー高さの整数倍チェック (0.60mm 単位)
        self.assertAlmostEqual(round(bb.size.Z / 0.60) * 0.60, bb.size.Z, places=3)

        bb_ft = self.fit_test.bounding_box()
        self.assertAlmostEqual(bb_ft.min.Z, 0.0, places=2)
        self.assertAlmostEqual(bb_ft.size.Z, FIT_TEST_HEIGHT, places=2)
        self.assertAlmostEqual(0.5 * (bb_ft.min.X + bb_ft.max.X), 0.0, places=2)
        self.assertAlmostEqual(0.5 * (bb_ft.min.Y + bb_ft.max.Y), 0.0, places=2)

    def test_02_rack_skirt_and_pipe_clearance_plus_active_preload(self) -> None:
        """薄鉄板フチと丸パイプに対し剛体Jフックが干渉ゼロであり、中央板バネが常時予圧と逃げ空間を持つこと."""
        z_shift = -HOLDER_BOTTOM_V
        skirt_phantom = Pos(0.0, -0.50 + MAIN_U_OFFSET, 0.5 * SKIRT_HEIGHT + z_shift) * Box(
            2.0 * HOOK_OUTER_HALF_SPAN + 10.0,
            1.00,
            SKIRT_HEIGHT,
        )
        self.assertAlmostEqual(_intersect_volume(self.holder, skirt_phantom), 0.0, places=2)

        # 左右の剛体Jフック領域 (|X| > HOOK_INNER_HALF_GAP) では丸パイプと完全非干渉
        for sign_x in (-1.0, +1.0):
            x_center = sign_x * 0.5 * (HOOK_INNER_HALF_GAP + HOOK_OUTER_HALF_SPAN)
            span_x = HOOK_OUTER_HALF_SPAN - HOOK_INNER_HALF_GAP - 0.4
            pipe_side = Pos(
                x_center,
                PIPE_CENTER_U + MAIN_U_OFFSET,
                PIPE_CENTER_V + z_shift,
            ) * (Rot(0.0, 90.0, 0.0) * Cylinder(PIPE_RADIUS, span_x))
            self.assertAlmostEqual(_intersect_volume(self.holder, pipe_side), 0.0, places=2)

        # 中央板バネ領域 (|X| < 7.5mm) では頂点越えディープフック35°斜面により常時予圧干渉 (>0.6mm) を持つこと
        self.assertLess(LATCH_TIP_U, PIPE_CENTER_U - 0.80)
        hook_slope = -1.0 / math.tan(math.radians(LATCH_OVERHANG_DEG))
        dist_pipe_to_ramp = abs(
            -hook_slope * (PIPE_CENTER_U - LATCH_TIP_U) + (PIPE_CENTER_V - LATCH_TIP_V)
        ) / math.sqrt(1.0 + hook_slope**2)
        self.assertGreater(PIPE_RADIUS - dist_pipe_to_ramp, 0.60)

        pipe_center_bay = Pos(
            0.0,
            PIPE_CENTER_U + MAIN_U_OFFSET,
            PIPE_CENTER_V + z_shift,
        ) * (Rot(0.0, 90.0, 0.0) * Cylinder(PIPE_RADIUS, 14.0))
        self.assertGreater(_intersect_volume(self.holder, pipe_center_bay), 2.0)

        # ステム背面のたわみ逃げポケット空間が完全に空いていること
        pocket_probe = Pos(
            0.0,
            LATCH_STEM_BACK_U + 0.5 * LATCH_POCKET_GAP + MAIN_U_OFFSET,
            2.0 + z_shift,
        ) * Box(14.0, LATCH_POCKET_GAP - 0.8, 12.0)
        self.assertAlmostEqual(_intersect_volume(self.holder, pocket_probe), 0.0, places=2)

    def test_03_front_finger_release_window_is_open(self) -> None:
        """第1段上のフロントアーチ窓が貫通し、手前からリリースタブへ指先が届くこと."""
        finger_probe = Pos(
            0.0,
            0.5 * (SPINE_REAR_U + SPINE_FRONT_U) + MAIN_U_OFFSET,
            45.0,
        ) * Box(20.0, (SPINE_FRONT_U - SPINE_REAR_U) + 6.0, 26.0)
        self.assertAlmostEqual(_intersect_volume(self.holder, finger_probe), 0.0, places=2)

    def test_04_four_standard_balls_seat_without_collision_or_rollout(self) -> None:
        """全4段に基準硬式球(φ67.0mm)が干渉なく着座し、上下球間隙>=7mmかつ前方転がり落ち防止を満たすこと."""
        r_std = STANDARD_BALL_DIA / 2.0
        z_centers = [compute_ball_center_z(idx, r_std) for idx in range(NUM_BALL_TIERS)]

        for idx, z_c in enumerate(z_centers):
            # 1. 着座位置 (+0.15mm 微小浮かせ) でホルダー全体と干渉ゼロ
            ball_rest = Pos(0.0, U_BALL_CENTER + MAIN_U_OFFSET, z_c + 0.15) * Sphere(r_std)
            self.assertAlmostEqual(
                _intersect_volume(self.holder, ball_rest),
                0.0,
                places=1,
                msg=f"Tier #{idx + 1} collided with standard ball at rest",
            )
            # 最下段ボール下端も Z=0 より上にあること
            self.assertGreater(z_c - r_std, 0.5)

            # 2. わずかに下 (-0.45mm) へ押し込むとテーパー座面と確実に接触すること
            ball_press = Pos(0.0, U_BALL_CENTER + MAIN_U_OFFSET, z_c - 0.45) * Sphere(r_std)
            self.assertGreater(
                _intersect_volume(self.holder, ball_press),
                1.0,
                msg=f"Tier #{idx + 1} failed to support standard ball",
            )

            # 3. 持ち上げずに手前 (+5.0mm) へ転がそうとするとC字アーム先端に阻まれること
            ball_roll = Pos(0.0, U_BALL_CENTER + 5.0 + MAIN_U_OFFSET, z_c) * Sphere(r_std)
            self.assertGreater(
                _intersect_volume(self.holder, ball_roll),
                2.0,
                msg=f"Tier #{idx + 1} failed to retain standard ball against forward roll",
            )

        # 4. 隣接する上下ボール間のクリアランスが 7.0mm 以上あること
        for idx in range(NUM_BALL_TIERS - 1):
            gap = (z_centers[idx + 1] - r_std) - (z_centers[idx] + r_std)
            self.assertGreaterEqual(gap, 7.0)

    def test_05_top_tier_supports_red_felt_and_red_foam_balls(self) -> None:
        """最上段(#4)がレッドフェルト球(φ75mm)とレッドスポンジ球(φ80mm)の両方を干渉なく安定保持すること."""
        top_idx = NUM_BALL_TIERS - 1
        for label, dia in (("red_felt_75", RED_FELT_BALL_DIA), ("red_foam_80", RED_FOAM_BALL_DIA)):
            r_red = dia / 2.0
            z_red = compute_ball_center_z(top_idx, r_red)

            ball_rest = Pos(0.0, U_BALL_CENTER + MAIN_U_OFFSET, z_red + 0.15) * Sphere(r_red)
            self.assertAlmostEqual(
                _intersect_volume(self.holder, ball_rest),
                0.0,
                places=1,
                msg=f"Top tier collided with {label} at rest",
            )

            ball_press = Pos(0.0, U_BALL_CENTER + MAIN_U_OFFSET, z_red - 0.45) * Sphere(r_red)
            self.assertGreater(
                _intersect_volume(self.holder, ball_press),
                1.0,
                msg=f"Top tier failed to support {label}",
            )

            ball_roll = Pos(0.0, U_BALL_CENTER + 5.0 + MAIN_U_OFFSET, z_red) * Sphere(r_red)
            self.assertGreater(
                _intersect_volume(self.holder, ball_roll),
                2.0,
                msg=f"Top tier failed to retain {label} against forward roll",
            )

    def test_06_ball_extraction_path_clears_upper_dishes(self) -> None:
        """1〜3段目の通常球を約10.5mm持ち上げて手前へ引き出す経路が上段皿やリブと一切干渉しないこと."""
        r_std = STANDARD_BALL_DIA / 2.0
        lift_z = 10.50
        for idx in range(NUM_BALL_TIERS - 1):
            z_c = compute_ball_center_z(idx, r_std)
            for du in (14.0, 28.0, 44.0):
                ball_extract = Pos(0.0, U_BALL_CENTER + du + MAIN_U_OFFSET, z_c + lift_z) * Sphere(r_std)
                self.assertAlmostEqual(
                    _intersect_volume(self.holder, ball_extract),
                    0.0,
                    places=1,
                    msg=f"Tier #{idx + 1} extraction collided at du={du}mm",
                )

    def test_07_support_free_overhangs_and_step_export(self) -> None:
        """Z>0.5mmに水平な下向き天井面が存在せず、本番・テストゲージ両STEPが正常に出力・再読込できること."""
        self.assertLessEqual(LATCH_OVERHANG_DEG, 55.1)
        for face in self.holder.faces():
            fb = face.bounding_box()
            if fb.min.Z > 0.50 and face.area > 4.0:
                normal = face.normal_at(face.center())
                # Z=-1.0 が真下向き水平天井; 56°オーバーハング上限なら normal.Z >= -cos(56°)=-0.559 ではなく
                # 鉛直からの角度 <= 56° すなわち |normal.Z| <= sin(90°-34°)=cos(34°)=0.829?
                # 注意: 鉛直壁は normal.Z = 0、45°オーバーハングは normal.Z = -0.7071、55°オーバーハング(鉛直から55°=水平から35°)は normal.Z = -cos(35°) = -0.8192
                self.assertGreaterEqual(
                    normal.Z,
                    -0.83,
                    msg=f"Steep unsupported overhang face detected at Z={fb.center().Z:.2f}, normal.Z={normal.Z:.3f}",
                )

        with tempfile.TemporaryDirectory() as tmpdir:
            main_step, fit_step = export_models(Path(tmpdir))
            self.assertTrue(main_step.exists())
            self.assertTrue(fit_step.exists())
            self.assertGreater(main_step.stat().st_size, 50_000)
            self.assertGreater(fit_step.stat().st_size, 10_000)

            reloaded_main = import_step(str(main_step))
            reloaded_fit = import_step(str(fit_step))
            self.assertEqual(len(reloaded_main.solids()), 1)
            self.assertEqual(len(reloaded_fit.solids()), 1)


if __name__ == "__main__":
    unittest.main()
