"""スピーカースタンド背面ルーターホルダー（v2 段付きC字フック仕様）の幾何・寸法・開口・STEP出力検証テスト."""

from pathlib import Path
import tempfile
import unittest
from build123d import Box, Pos, import_step

try:
    from speaker_stand_router_holder.speaker_stand_router_holder import (
        FIT_TEST_WIDTH,
        HOLDER_WIDTH,
        HOOK_OVERHANG_REACH,
        ROUTER_CHAMBER_HEIGHT,
        SPINE_INNER_REACH,
        STAND_TRAY_INNER_DEPTH,
        TOP_LIP_DEPTH,
        TOP_PLATE_OVERHANG,
        TOP_PLATE_SLOT_GAP,
        TOTAL_DEPTH,
        TOTAL_HEIGHT,
        build_fit_test_piece,
        build_router_holder,
        export_models,
    )
except ModuleNotFoundError:
    from speaker_stand_router_holder import (  # type: ignore[no-redef]
        FIT_TEST_WIDTH,
        HOLDER_WIDTH,
        HOOK_OVERHANG_REACH,
        ROUTER_CHAMBER_HEIGHT,
        SPINE_INNER_REACH,
        STAND_TRAY_INNER_DEPTH,
        TOP_LIP_DEPTH,
        TOP_PLATE_OVERHANG,
        TOP_PLATE_SLOT_GAP,
        TOTAL_DEPTH,
        TOTAL_HEIGHT,
        build_fit_test_piece,
        build_router_holder,
        export_models,
    )


def _intersection_volume(part_a, part_b) -> float:
    """2つの形状の共通部分体積を返す（非干渉なら 0.0）."""
    inter = part_a & part_b
    if inter is None:
        return 0.0
    solids = inter.solids()
    return sum(s.volume for s in solids)


class TestSpeakerStandRouterHolder(unittest.TestCase):
    """本番モデルおよび嵌合テストピース（v2 段付きC字フック仕様）の仕様適合テスト."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.holder = build_router_holder()
        cls.fit_test = build_fit_test_piece()

    def test_holder_is_single_valid_closed_solid(self) -> None:
        solids = self.holder.solids()
        self.assertEqual(len(solids), 1, "本番モデルは単一ソリッドである必要があります")
        self.assertTrue(solids[0].is_valid, "本番モデルソリッドが invalid です")
        self.assertGreater(solids[0].volume, 50_000.0, "体積が想定より小さすぎます")

    def test_holder_print_orientation_and_bounding_box(self) -> None:
        bb = self.holder.bounding_box()
        # Z=0 ビルドプレート接地 & Z=144.0mm (0.30mm * 480層)
        self.assertAlmostEqual(bb.min.Z, 0.0, places=3)
        self.assertAlmostEqual(bb.max.Z, HOLDER_WIDTH, places=2)
        self.assertAlmostEqual(bb.size.Z, 144.0, places=2)

        # XY外寸: 236.6mm x 89.5mm (中心(0,0)付近、Bambu Lab P2S 256x256mm以内)
        self.assertAlmostEqual(TOTAL_HEIGHT, 236.6, places=2)
        self.assertAlmostEqual(SPINE_INNER_REACH, 83.5, places=2)
        self.assertAlmostEqual(TOTAL_DEPTH, 89.5, places=2)
        self.assertAlmostEqual(bb.size.X, TOTAL_HEIGHT, delta=0.1)
        self.assertAlmostEqual(bb.size.Y, TOTAL_DEPTH, delta=0.1)
        self.assertAlmostEqual((bb.min.X + bb.max.X) / 2.0, 0.0, delta=0.1)
        self.assertAlmostEqual((bb.min.Y + bb.max.Y) / 2.0, 0.0, delta=0.1)
        self.assertLess(bb.size.X, 250.0)
        self.assertLess(bb.size.Y, 250.0)
        self.assertLess(bb.size.Z, 250.0)

    def test_stepped_c_hook_slot_and_61mm_overhang_fit(self) -> None:
        # 1. 天板噛み合い溝 (ソリッド部 Y=+10.0, Z=72.0 および 連続枠上 Y=-10.0, Z=9.0) のX方向内寸が 15.80mm であること
        for py, pz in ((10.0, 72.0), (-10.0, 9.0)):
            probe = Pos(-105.6, py, pz) * Box(24.0, 0.5, 0.5)
            void_in_slot = probe - self.holder
            slot_solids = [
                s for s in void_in_slot.solids() if abs(s.center().X - (-105.6)) < 3.0
            ]
            self.assertEqual(len(slot_solids), 1)
            self.assertAlmostEqual(
                slot_solids[0].bounding_box().size.X, TOP_PLATE_SLOT_GAP, delta=0.05
            )

        # 2. 支柱当てパッド前端(bb.min.Y = -44.75) から Cフック奥壁(Y=+16.75) までのリーチが 61.50mm であること
        self.assertAlmostEqual(TOP_PLATE_OVERHANG, 61.0, places=2)
        self.assertAlmostEqual(HOOK_OVERHANG_REACH, 61.5, places=2)
        bb = self.holder.bounding_box()
        slot_back_probe = Pos(-105.6, 15.0, 72.0) * Box(10.0, 10.0, 1.0)
        slot_void = slot_back_probe - self.holder
        back_y = max(s.bounding_box().max.Y for s in slot_void.solids())
        self.assertAlmostEqual(back_y - bb.min.Y, HOOK_OVERHANG_REACH, delta=0.05)

        # 3. 天板上面ツメ長さが 52.00mm (実効天板かかり代 51.50mm) 確保されていること
        self.assertAlmostEqual(TOP_LIP_DEPTH, 52.0, places=2)
        lip_probe = Pos(-115.9, -5.0, 72.0) * Box(1.0, 70.0, 1.0)
        lip_inter = self.holder & lip_probe
        self.assertIsNotNone(lip_inter)
        lip_min_y = lip_inter.bounding_box().min.Y
        self.assertAlmostEqual(back_y - lip_min_y, TOP_LIP_DEPTH, delta=0.05)

        # 4. 実測 15.5mm厚×奥行235mm天板(背面張り出し61.0mm: Y in [-218.75, +16.25]) および
        #    木製支柱(奥行116.6mm: Y in [-161.36, -44.76]) と一切干渉しないこと
        simulated_top_plate = Pos(-105.6, -101.25, 72.0) * Box(15.5, 235.0, 183.0)
        simulated_pillar = Pos(11.1, -103.06, 72.0) * Box(217.8, 116.6, 113.8)
        self.assertAlmostEqual(
            _intersection_volume(self.holder, simulated_top_plate), 0.0, places=2
        )
        self.assertAlmostEqual(
            _intersection_volume(self.holder, simulated_pillar), 0.0, places=2
        )

    def test_router_chamber_and_stand_tray_clearances(self) -> None:
        # 1. 底面U字トレイのY方向内寸が 77.00mm (中心 Y=+0.25, X=+105.0, Z=72.0) であること
        tray_probe = Pos(105.0, 0.25, 72.0) * Box(0.5, 86.0, 0.5)
        tray_void = tray_probe - self.holder
        inner_solids = [
            s for s in tray_void.solids() if abs(s.center().Y - 0.25) < 5.0
        ]
        self.assertEqual(len(inner_solids), 1)
        self.assertAlmostEqual(
            inner_solids[0].bounding_box().size.Y, STAND_TRAY_INNER_DEPTH, delta=0.05
        )
        self.assertAlmostEqual(STAND_TRAY_INNER_DEPTH, 77.0, places=2)

        # 2. ルーター収容空間のX方向有効高さが 204.00mm (Y=+20.0, Z=9.0 ソリッド枠上) であること
        chamber_probe = Pos(10.3, 20.0, 9.0) * Box(214.0, 0.5, 0.5)
        chamber_void = chamber_probe - self.holder
        chamber_solids = [
            s for s in chamber_void.solids() if abs(s.center().X - 10.3) < 5.0
        ]
        self.assertEqual(len(chamber_solids), 1)
        self.assertAlmostEqual(
            chamber_solids[0].bounding_box().size.X, ROUTER_CHAMBER_HEIGHT, delta=0.05
        )

        # 3. ルーター付属スタンド(実測75mm / NEC公称76mm × 高さ11mm)＋本体(厚55mm×全高197mm)が非干渉で収まること
        sim_stand = Pos(106.5, 0.25, 72.0) * Box(11.0, 76.0, 184.0)
        sim_body = Pos(13.5, 0.25, 72.0) * Box(186.0, 55.0, 213.5)
        self.assertAlmostEqual(
            _intersection_volume(self.holder, sim_stand), 0.0, places=2
        )
        self.assertAlmostEqual(
            _intersection_volume(self.holder, sim_body), 0.0, places=2
        )

    def test_pentagon_windows_solid_shoulder_and_end_frames(self) -> None:
        # 背面3窓の中心(X = -53.7, +10.3, +74.3, Y = +41.75, Z = 60.0)が貫通していること
        for wx in (-53.7, 10.3, 74.3):
            ray = Pos(wx, 41.75, 60.0) * Box(2.0, 12.0, 2.0)
            self.assertAlmostEqual(
                _intersection_volume(self.holder, ray),
                0.0,
                places=2,
                msg=f"背面窓 X={wx} が貫通していません",
            )

        # 背面窓の間の垂直太柱(X = -21.7, +42.3, Z = 60.0)はソリッドであること
        for px in (-21.7, 42.3):
            ray = Pos(px, 41.75, 60.0) * Box(2.0, 12.0, 2.0)
            self.assertGreater(
                _intersection_volume(self.holder, ray),
                10.0,
                msg=f"背面太柱 X={px} が存在しません",
            )

        # 底面トレイ窓(Y = +0.25, Z = 60.0) と 天板裏フロントアーム窓(Y = -11.25, Z = 60.0) が貫通していること
        bottom_ray = Pos(115.3, 0.25, 60.0) * Box(12.0, 2.0, 2.0)
        under_arm_ray = Pos(-94.7, -11.25, 60.0) * Box(12.0, 2.0, 2.0)
        self.assertAlmostEqual(
            _intersection_volume(self.holder, bottom_ray), 0.0, places=2
        )
        self.assertAlmostEqual(
            _intersection_volume(self.holder, under_arm_ray), 0.0, places=2
        )

        # Cフック奥壁〜背面スパイン間の荷重伝達ショルダー部(X = -94.7, Y = +28.0, Z = 60.0)は無開口ソリッドであること
        shoulder_ray = Pos(-94.7, 28.0, 60.0) * Box(6.0, 10.0, 2.0)
        self.assertGreater(_intersection_volume(self.holder, shoulder_ray), 80.0)

        # 天板上面ツメ(X = -115.9, Y = -10.0, Z = 60.0) は開口無しソリッドであること
        top_lip_ray = Pos(-115.9, -10.0, 60.0) * Box(8.0, 2.0, 2.0)
        self.assertGreater(_intersection_volume(self.holder, top_lip_ray), 5.0)

        # 下部連続枠(Z = 9.0) と 上部連続枠(Z = 135.0) は窓位置(X = +10.3)でもソリッドであること
        for fz in (9.0, 135.0):
            frame_ray = Pos(10.3, 41.75, fz) * Box(2.0, 12.0, 2.0)
            self.assertGreater(
                _intersection_volume(self.holder, frame_ray),
                10.0,
                msg=f"連続枠 Z={fz} が途切れています",
            )

    def test_fit_test_piece_and_step_export_roundtrip(self) -> None:
        solids = self.fit_test.solids()
        self.assertEqual(len(solids), 1)
        self.assertTrue(solids[0].is_valid)
        bb = self.fit_test.bounding_box()
        self.assertAlmostEqual(bb.min.Z, 0.0, places=3)
        self.assertAlmostEqual(bb.max.Z, FIT_TEST_WIDTH, places=2)
        self.assertAlmostEqual(bb.size.Y, TOTAL_DEPTH, delta=0.1)

        with tempfile.TemporaryDirectory() as tmpdir:
            main_path, fit_path = export_models(Path(tmpdir))
            self.assertTrue(main_path.exists())
            self.assertTrue(fit_path.exists())
            reloaded_main = import_step(str(main_path))
            reloaded_fit = import_step(str(fit_path))
            self.assertAlmostEqual(
                reloaded_main.volume,
                self.holder.volume,
                delta=self.holder.volume * 0.002,
            )
            self.assertAlmostEqual(
                reloaded_fit.volume,
                self.fit_test.volume,
                delta=self.fit_test.volume * 0.002,
            )


if __name__ == "__main__":
    unittest.main()
