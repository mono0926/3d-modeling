"""スチールラック共通マウントフック (steel_rack_base_hook) の単体幾何・物理検証テスト."""

import math
import tempfile
import unittest
from pathlib import Path
from build123d import Box, Cylinder, Pos, Rot, import_step

from steel_rack_base_hook import (
    FIT_TEST_HEIGHT,
    FIT_TEST_WIDTH,
    HOLDER_BOTTOM_V,
    HOOK_INNER_HALF_GAP,
    HOOK_REAR_BACK_U,
    LATCH_OVERHANG_DEG,
    LATCH_POCKET_GAP,
    LATCH_POCKET_REAR_U,
    LATCH_STEM_BACK_U,
    LATCH_TIP_U,
    LATCH_TIP_V,
    PIPE_CENTER_U,
    PIPE_CENTER_V,
    PIPE_RADIUS,
    SKIRT_HEIGHT,
    build_steel_rack_fit_test_piece,
    build_steel_rack_mounting_core,
    export_models,
)


def _intersect_volume(part_a, part_b) -> float:
    common = part_a & part_b
    if common is None:
        return 0.0
    return sum(s.volume for s in common.solids())


class TestSteelRackBaseHook(unittest.TestCase):
    """実機検証済み v4 スチールラック共通フックの多様体・寸法・非干渉・常時予圧・STEP出力を検証する."""

    def test_01_base_hook_and_fit_test_are_valid_single_solids(self) -> None:
        """標準嵌合テストピースと設計座標/Z=0配置コアがいずれも単一多様体ソリッドであること."""
        core_uv = build_steel_rack_mounting_core(outer_half_span=33.80, spine_thickness=4.80, align_bottom_to_z0=False)
        core_z0 = build_steel_rack_mounting_core(outer_half_span=33.80, spine_thickness=4.80, align_bottom_to_z0=True)
        fit_piece = build_steel_rack_fit_test_piece(spine_thickness=4.80)

        for solid in (core_uv, core_z0, fit_piece):
            self.assertTrue(solid.is_valid)
            self.assertEqual(len(solid.solids()), 1)

        self.assertAlmostEqual(core_uv.bounding_box().min.Z, HOLDER_BOTTOM_V, places=2)
        self.assertAlmostEqual(core_z0.bounding_box().min.Z, 0.0, places=2)

        bb_ft = fit_piece.bounding_box()
        self.assertAlmostEqual(bb_ft.min.Z, 0.0, places=2)
        self.assertAlmostEqual(bb_ft.size.X, FIT_TEST_WIDTH, places=2)
        self.assertAlmostEqual(bb_ft.size.Y, (LATCH_POCKET_REAR_U + 4.80) - HOOK_REAR_BACK_U, places=2)
        self.assertAlmostEqual(bb_ft.size.Z, FIT_TEST_HEIGHT, places=2)
        self.assertAlmostEqual(0.5 * (bb_ft.min.X + bb_ft.max.X), 0.0, places=2)
        self.assertAlmostEqual(0.5 * (bb_ft.min.Y + bb_ft.max.Y), 0.0, places=2)

    def test_02_rack_skirt_and_pipe_zero_clearance_collision_and_preload(self) -> None:
        """薄鉄板フチ・丸パイプに対し剛体Jフックが干渉ゼロで、中央板バネが常時予圧(>0.6mm)を持つこと."""
        outer_half = 34.00
        core = build_steel_rack_mounting_core(outer_half_span=outer_half, spine_thickness=6.60, align_bottom_to_z0=True)
        z_shift = -HOLDER_BOTTOM_V

        skirt = Pos(0.0, -0.50, 0.5 * SKIRT_HEIGHT + z_shift) * Box(2.0 * outer_half + 10.0, 1.00, SKIRT_HEIGHT)
        self.assertAlmostEqual(_intersect_volume(core, skirt), 0.0, places=2)

        for sign_x in (-1.0, +1.0):
            x_c = sign_x * 0.5 * (HOOK_INNER_HALF_GAP + outer_half)
            span_x = outer_half - HOOK_INNER_HALF_GAP - 0.4
            pipe_side = Pos(x_c, PIPE_CENTER_U, PIPE_CENTER_V + z_shift) * (
                Rot(0.0, 90.0, 0.0) * Cylinder(PIPE_RADIUS, span_x)
            )
            self.assertAlmostEqual(_intersect_volume(core, pipe_side), 0.0, places=2)

        hook_slope = -1.0 / math.tan(math.radians(LATCH_OVERHANG_DEG))
        dist_pipe_to_ramp = abs(
            -hook_slope * (PIPE_CENTER_U - LATCH_TIP_U) + (PIPE_CENTER_V - LATCH_TIP_V)
        ) / math.sqrt(1.0 + hook_slope**2)
        self.assertGreater(PIPE_RADIUS - dist_pipe_to_ramp, 0.60)

        pocket_probe = Pos(0.0, LATCH_STEM_BACK_U + 0.5 * LATCH_POCKET_GAP, 2.0 + z_shift) * Box(
            14.0, LATCH_POCKET_GAP - 0.8, 12.0
        )
        self.assertAlmostEqual(_intersect_volume(core, pocket_probe), 0.0, places=2)

    def test_03_parametric_outer_span_and_spine_thickness(self) -> None:
        """アタッチメント側パラメーター(外幅・背板厚)に応じて正確に外寸が変化すること."""
        c_racket = build_steel_rack_mounting_core(outer_half_span=33.80, spine_thickness=4.80)
        c_ball = build_steel_rack_mounting_core(outer_half_span=34.00, spine_thickness=6.60)

        self.assertAlmostEqual(c_racket.bounding_box().size.X, 67.60, places=2)
        self.assertAlmostEqual(c_ball.bounding_box().size.X, 68.00, places=2)
        self.assertAlmostEqual(c_ball.bounding_box().size.Y - c_racket.bounding_box().size.Y, 1.80, places=2)

    def test_04_step_export_roundtrip(self) -> None:
        """単体確認用STEPファイルが正常に出力・再読込できること."""
        with tempfile.TemporaryDirectory() as tmpdir:
            step_path = export_models(Path(tmpdir))
            self.assertTrue(step_path.exists())
            self.assertGreater(step_path.stat().st_size, 10_000)
            reloaded = import_step(str(step_path))
            self.assertEqual(len(reloaded.solids()), 1)


if __name__ == "__main__":
    unittest.main()
