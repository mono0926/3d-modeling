"""スチールラック用 テニスラケット掛け（2機種兼用・v2実機適合版）の自動幾何・公差・ばね力学・運動学・STEP検証テスト."""

import math
from pathlib import Path
import tempfile
import unittest
from build123d import (
    Box,
    Cylinder,
    GeomType,
    Plane,
    Pos,
    Rot,
    import_step,
)

try:
    from steel_rack_tennis_racket_holder.steel_rack_tennis_racket_holder import (
        CRADLE_GROOVE_DEPTH,
        CRADLE_INNER_BACK_U,
        CRADLE_TOTAL_HEIGHT,
        FIT_TEST_HEIGHT,
        FIT_TEST_U_OFFSET,
        FIT_TEST_WIDTH,
        HOLDER_BOTTOM_V,
        HOLDER_TOP_V,
        HOOK_INNER_HALF_GAP,
        HOOK_OUTER_HALF_SPAN,
        HOOK_WIDTH,
        J_FLOOR_TOP_V,
        J_FRONT_INNER_U,
        LATCH_LEAF_SPAN_U,
        LATCH_LEAF_THICKNESS,
        LATCH_POCKET_REAR_U,
        LATCH_STEM_BACK_U,
        LATCH_STEM_FRONT_U,
        LATCH_STEM_THICKNESS,
        LATCH_TIP_U,
        LATCH_TIP_V,
        LATCH_WIDTH,
        MAIN_U_OFFSET,
        PIPE_CENTER_U,
        PIPE_CENTER_V,
        PIPE_CLEARANCE_FROM_SKIRT_U,
        PIPE_DIA,
        PIPE_GAP_TO_SKIRT_V,
        SKIRT_HEIGHT,
        STOPPER_FRONT_U,
        STOPPER_TOP_V,
        build_fit_test_piece,
        build_holder,
        export_models,
    )
except ModuleNotFoundError:
    from steel_rack_tennis_racket_holder import (  # type: ignore[no-redef]
        CRADLE_GROOVE_DEPTH,
        CRADLE_INNER_BACK_U,
        CRADLE_TOTAL_HEIGHT,
        FIT_TEST_HEIGHT,
        FIT_TEST_U_OFFSET,
        FIT_TEST_WIDTH,
        HOLDER_BOTTOM_V,
        HOLDER_TOP_V,
        HOOK_INNER_HALF_GAP,
        HOOK_OUTER_HALF_SPAN,
        HOOK_WIDTH,
        J_FLOOR_TOP_V,
        J_FRONT_INNER_U,
        LATCH_LEAF_SPAN_U,
        LATCH_LEAF_THICKNESS,
        LATCH_POCKET_REAR_U,
        LATCH_STEM_BACK_U,
        LATCH_STEM_FRONT_U,
        LATCH_STEM_THICKNESS,
        LATCH_TIP_U,
        LATCH_TIP_V,
        LATCH_WIDTH,
        MAIN_U_OFFSET,
        PIPE_CENTER_U,
        PIPE_CENTER_V,
        PIPE_CLEARANCE_FROM_SKIRT_U,
        PIPE_DIA,
        PIPE_GAP_TO_SKIRT_V,
        SKIRT_HEIGHT,
        STOPPER_FRONT_U,
        STOPPER_TOP_V,
        build_fit_test_piece,
        build_holder,
        export_models,
    )


def _intersection_volume(shape_a, shape_b) -> float:
    """2つの3D形状のブーリアン積体積 (mm^3) を安全に算出する."""
    common = shape_a & shape_b
    if common is None:
        return 0.0
    solids = common.solids()
    return float(sum(s.volume for s in solids)) if solids else 0.0


def _u_to_y(u: float, u_offset: float = MAIN_U_OFFSET) -> float:
    """設計座標 u (棚板垂直面 u=0, 手前 +u) を造形座標 Y へ変換する."""
    return u + u_offset


def _v_to_z(v: float) -> float:
    """設計座標 v (棚板下端 v=0) を造形座標 Z (Z=0 接地) へ変換する."""
    return v - HOLDER_BOTTOM_V


def _make_rack_3d(
    u_offset: float,
    skirt_t: float = 1.05,
    gap_u: float = 2.00,
    gap_v: float = 2.00,
    du_holder: float = 0.0,
    dv_holder: float = 0.0,
    span_x: float = 140.0,
):
    """ホルダー座標系に対する実機スチールラック（薄鉄板フチ＋前方φ7.2mm丸パイプ）3D形状を生成する.

    ホルダー自体がラックに対して (+du_holder, +dv_holder) 動くことは、
    ホルダー固定座標系においてラックが (-du_holder, -dv_holder) 動くことと等価。
    """
    u_shift = -du_holder
    v_shift = -dv_holder

    skirt = Pos(
        0.0,
        _u_to_y(-skirt_t / 2.0 + u_shift, u_offset),
        _v_to_z(SKIRT_HEIGHT / 2.0 + v_shift),
    ) * Box(span_x, skirt_t, SKIRT_HEIGHT)

    shelf_top = Pos(
        0.0,
        _u_to_y(-25.0 + u_shift, u_offset),
        _v_to_z(SKIRT_HEIGHT - 0.525 + v_shift),
    ) * Box(span_x, 50.0, 1.05)

    pc_u = gap_u + PIPE_DIA / 2.0 + u_shift
    pc_v = -(gap_v + PIPE_DIA / 2.0) + v_shift
    pipe = (
        Pos(0.0, _u_to_y(pc_u, u_offset), _v_to_z(pc_v))
        * Rot(0, 90, 0)
        * Cylinder(PIPE_DIA / 2.0, span_x)
    )
    return skirt + shelf_top, pipe


class TestSteelRackTennisRacketHolder(unittest.TestCase):
    """v2 実機ラック配置（丸パイプ前方クリアランス2mm）および本物の板バネラッチ検証スイート."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.holder = build_holder()
        cls.fit_test = build_fit_test_piece()

    def test_01_true_rack_constants_and_valid_grounded_solids(self) -> None:
        """丸パイプが棚板垂直面(u=0)から2.0mm手前(u=+2.0〜+9.2mm)に定義され、単一ソリッドがZ=0接地すること."""
        self.assertAlmostEqual(PIPE_CLEARANCE_FROM_SKIRT_U, 2.00, places=2)
        self.assertAlmostEqual(PIPE_GAP_TO_SKIRT_V, 2.00, places=2)
        self.assertAlmostEqual(PIPE_CENTER_U, +5.60, places=2)
        self.assertAlmostEqual(PIPE_CENTER_V, -5.60, places=2)

        for name, part in (("holder", self.holder), ("fit_test", self.fit_test)):
            with self.subTest(part=name):
                self.assertTrue(part.is_valid, f"{name} must be valid")
                self.assertEqual(len(part.solids()), 1, f"{name} must be 1 single watertight solid")
                self.assertGreater(part.volume, 2000.0)

                bb = part.bounding_box()
                self.assertAlmostEqual(bb.min.Z, 0.0, places=2)
                self.assertAlmostEqual((bb.min.X + bb.max.X) / 2.0, 0.0, places=2)
                self.assertAlmostEqual((bb.min.Y + bb.max.Y) / 2.0, 0.0, places=2)
                # 0.20mm / 0.30mm レイヤー両対応 (0.60mm 整数倍)
                self.assertAlmostEqual(bb.size.Z % 0.60, 0.0, places=2)

        bb_main = self.holder.bounding_box()
        self.assertGreaterEqual(bb_main.size.X, 112.0)
        self.assertLessEqual(bb_main.size.X, 124.0)
        self.assertAlmostEqual(bb_main.size.Z, CRADLE_TOTAL_HEIGHT, places=2)

        bb_fit = self.fit_test.bounding_box()
        self.assertAlmostEqual(bb_fit.size.X, FIT_TEST_WIDTH, places=2)
        self.assertAlmostEqual(bb_fit.size.Z, FIT_TEST_HEIGHT, places=2)
        # 底面板バネ厚みも 0.60mm 整数倍 (1.80mm) であること
        self.assertAlmostEqual(LATCH_LEAF_THICKNESS % 0.60, 0.0, places=2)

    def test_02_multi_tolerance_rack_fit_and_zero_shelf_top_protrusion(self) -> None:
        """前後・上下クリアランスが 1.5〜2.5mm に変動しても左右Jフックが無干渉で着座しラッチが確実に掛かること."""
        tolerance_cases = [
            ("Min(1.5,1.5)", 0.95, 1.50, 1.50),
            ("Nom(2.0,2.0)", 1.05, 2.00, 2.00),
            ("Max(2.5,2.5)", 1.20, 2.50, 2.50),
            ("Mix(1.5,2.5)", 1.05, 1.50, 2.50),
            ("Mix(2.5,1.5)", 1.05, 2.50, 1.50),
        ]
        C_line = LATCH_TIP_U + LATCH_TIP_V  # 45° ラッチ下面 u + v = C

        for name, part, u_off in (
            ("holder", self.holder, MAIN_U_OFFSET),
            ("fit_test", self.fit_test, FIT_TEST_U_OFFSET),
        ):
            # 左右の剛体Jフック領域 (|X| >= HOOK_INNER_HALF_GAP) のみを切り出して剛体非干渉を厳密検証
            left_mask = Pos(-50.0 - HOOK_INNER_HALF_GAP, 0.0, 50.0) * Box(100.0, 200.0, 120.0)
            right_mask = Pos(+50.0 + HOOK_INNER_HALF_GAP, 0.0, 50.0) * Box(100.0, 200.0, 120.0)
            rigid_hooks = (part & left_mask) + (part & right_mask)

            for case_label, skirt_t, gap_u, gap_v in tolerance_cases:
                with self.subTest(part=name, case=case_label):
                    # お辞儀モーメントでJフック背面ストッパー(STOPPER_FRONT_U)が薄鉄板裏面(-skirt_t)に当接する位置
                    du_seat = -skirt_t - STOPPER_FRONT_U
                    pc_u_in_h = (gap_u + PIPE_DIA / 2.0) - du_seat
                    pc_v_in_h = -(gap_v + PIPE_DIA / 2.0)
                    # 45°ラッチ下面がパイプ上肩 (+45°) に着座する上下位置 dv_seat
                    dv_seat = (pc_u_in_h + pc_v_in_h + (PIPE_DIA / 2.0) * math.sqrt(2.0)) - C_line

                    shelf, pipe = _make_rack_3d(
                        u_off,
                        skirt_t=skirt_t,
                        gap_u=gap_u,
                        gap_v=gap_v,
                        du_holder=du_seat,
                        dv_holder=dv_seat,
                    )
                    self.assertAlmostEqual(
                        _intersection_volume(rigid_hooks, shelf),
                        0.0,
                        places=2,
                        msg=f"{name} rigid J-hooks must clear shelf at {case_label}",
                    )
                    self.assertAlmostEqual(
                        _intersection_volume(rigid_hooks, pipe),
                        0.0,
                        places=2,
                        msg=f"{name} rigid J-hooks must clear pipe at {case_label}",
                    )

                    # ラッチ先端 (LATCH_TIP_U) が丸パイプ手前端よりも 1.60mm 以上奥までしっかり掛かること
                    pipe_front_in_h = pc_u_in_h + PIPE_DIA / 2.0
                    latch_overlap = pipe_front_in_h - LATCH_TIP_U
                    self.assertGreaterEqual(latch_overlap, 1.60)
                    self.assertLessEqual(latch_overlap, 3.15)

                    # カチッとラッチが掛かる瞬間に底面床 (J_FLOOR_TOP_V) がパイプ下端に当たらず >=1.0mm 余裕があること
                    overtravel_margin = (pc_v_in_h - PIPE_DIA / 2.0) - (J_FLOOR_TOP_V + dv_seat)
                    self.assertGreaterEqual(overtravel_margin, 1.00)

                    # 裏ストッパー上端が薄鉄板裏面に十分掛かりつつ、棚板天面 (+18.10mm) より十分下にあること
                    stopper_engaged_v = STOPPER_TOP_V + dv_seat
                    self.assertGreaterEqual(stopper_engaged_v, 6.50)
                    self.assertLessEqual(stopper_engaged_v, SKIRT_HEIGHT - 6.00)

    def test_03_straight_up_installation_without_excluded_points(self) -> None:
        """左右の剛体フレーム全体が傾き0°のまま真下(dv=-24mm)から着座位置まで一切干渉せず直進進入できること."""
        for name, part, u_off in (
            ("holder", self.holder, MAIN_U_OFFSET),
            ("fit_test", self.fit_test, FIT_TEST_U_OFFSET),
        ):
            left_mask = Pos(-50.0 - HOOK_INNER_HALF_GAP, 0.0, 50.0) * Box(100.0, 200.0, 120.0)
            right_mask = Pos(+50.0 + HOOK_INNER_HALF_GAP, 0.0, 50.0) * Box(100.0, 200.0, 120.0)
            rigid_frame = (part & left_mask) + (part & right_mask)

            # 真下 dv = -24mm から dv = 0mm まで 2.0mm 刻みで全ステップ完全無干渉であることを3Dブーリアンで直接証明
            du_insert = -1.05 - STOPPER_FRONT_U - 0.15  # 薄鉄板裏に 0.15mm 余裕を持たせた直進ライン
            for dv in (-24.0, -20.0, -16.0, -12.0, -8.0, -4.0, -2.0, 0.0):
                shelf, pipe = _make_rack_3d(
                    u_off,
                    skirt_t=1.05,
                    gap_u=2.00,
                    gap_v=2.00,
                    du_holder=du_insert,
                    dv_holder=dv,
                )
                self.assertAlmostEqual(
                    _intersection_volume(rigid_frame, shelf + pipe),
                    0.0,
                    places=2,
                    msg=f"{name} rigid frame must slide straight up at dv={dv}mm with zero collision",
                )

    def test_04_isolated_cantilever_spring_pocket_and_ergonomic_force(self) -> None:
        """中央板バネが左右スリットと背面ポケットで完全に独立しており、押し込み力が約1.2〜2.5kgfであること."""
        for name, part, u_off in (
            ("holder", self.holder, MAIN_U_OFFSET),
            ("fit_test", self.fit_test, FIT_TEST_U_OFFSET),
        ):
            with self.subTest(part=name):
                # 1. 左右の分離スリット (X = ±(LATCH_WIDTH/2 + 1.0)) が u = -1.5 〜 +18.0 で完全に貫通空間であること
                slot_x = LATCH_WIDTH / 2.0 + 0.95
                slot_u_len = LATCH_POCKET_REAR_U - (-1.50) - 0.40
                slot_u_mid = 0.5 * (-1.50 + LATCH_POCKET_REAR_U - 0.40)
                for sgn in (-1.0, 1.0):
                    slot_probe = Pos(
                        sgn * slot_x,
                        _u_to_y(slot_u_mid, u_off),
                        _v_to_z(-2.0),
                    ) * Box(1.20, slot_u_len, 24.0)
                    self.assertAlmostEqual(
                        _intersection_volume(part, slot_probe),
                        0.0,
                        places=2,
                        msg=f"{name} side isolation slot must be 100% open air so spring never fuses to J-hooks",
                    )

                # 2. 垂直ステム背面のたわみ逃げポケット (u = LATCH_STEM_BACK_U+0.2 .. LATCH_POCKET_REAR_U-0.2) が完全空間であること
                pocket_u_len = (LATCH_POCKET_REAR_U - LATCH_STEM_BACK_U) - 0.40
                self.assertGreaterEqual(
                    LATCH_POCKET_REAR_U - LATCH_STEM_BACK_U,
                    4.60,
                    "Spring deflection pocket must be >= 4.6mm deep so stem never bottoms out during snap",
                )
                pocket_u_mid = 0.5 * (LATCH_STEM_BACK_U + LATCH_POCKET_REAR_U)
                pocket_probe = Pos(
                    0.0,
                    _u_to_y(pocket_u_mid, u_off),
                    _v_to_z(-3.0),
                ) * Box(LATCH_WIDTH, pocket_u_len, 22.0)
                self.assertAlmostEqual(
                    _intersection_volume(part, pocket_probe),
                    0.0,
                    places=2,
                    msg=f"{name} rear deflection pocket behind latch stem must be 100% unobstructed",
                )

                # 3. パイプ真下の底面板バネの上側 (v = -13.0 .. -9.5) も完全空間であり、v1のような塊でないこと
                above_leaf_probe = Pos(
                    0.0,
                    _u_to_y(0.5 * (-1.0 + LATCH_TIP_U - 0.5), u_off),
                    _v_to_z(-11.2),
                ) * Box(LATCH_WIDTH, (LATCH_TIP_U - 0.5) - (-1.0), 3.2)
                self.assertAlmostEqual(
                    _intersection_volume(part, above_leaf_probe),
                    0.0,
                    places=2,
                    msg=f"{name} space above Z=0 horizontal leaf spring must be open air (not a solid brick)",
                )

        # 4. Castigliano エネルギー法による実効ばね定数・押し込み荷重・層間応力の物理検証 (PETG & PLA)
        L_h = LATCH_LEAF_SPAN_U
        L_v = LATCH_TIP_V - (HOLDER_BOTTOM_V + LATCH_LEAF_THICKNESS / 2.0)
        I_h = LATCH_WIDTH * (LATCH_LEAF_THICKNESS**3) / 12.0
        I_v = LATCH_WIDTH * (LATCH_STEM_THICKNESS**3) / 12.0
        delta_nom = (PIPE_CENTER_U + PIPE_DIA / 2.0) - 0.20 - LATCH_TIP_U  # 標準着座押し込み量 (~2.30mm)

        for mat, E_mpa, f_min_n, f_max_n in (
            ("PETG", 2100.0, 10.0, 19.0),
            ("PLA", 3000.0, 14.0, 26.0),
        ):
            compliance = (L_v**3) / (3.0 * E_mpa * I_v) + (L_v**2) * L_h / (E_mpa * I_h)
            k_n_per_mm = 1.0 / compliance
            f_nom = k_n_per_mm * delta_nom
            sig_v_z = (f_nom * L_v) * (LATCH_STEM_THICKNESS / 2.0) / I_v
            eps_h_pct = ((f_nom * L_v) * (LATCH_LEAF_THICKNESS / 2.0) / I_h) / E_mpa * 100.0

            self.assertGreaterEqual(f_nom, f_min_n, f"{mat} snap force too weak")
            self.assertLessEqual(f_nom, f_max_n, f"{mat} snap force too stiff for hand installation")
            self.assertLess(sig_v_z, 14.0, f"{mat} Z-layer tensile stress must stay well below delamination")
            self.assertLess(eps_h_pct, 1.30, f"{mat} Z=0 leaf strain must remain purely elastic")

    def test_05_both_rackets_fit_in_cradle_and_clear_shelf(self) -> None:
        """CLASH 26 V3.0 と HEAD EXTREME MP 2026 の双方がV字溝に安定着座し棚板・パイプと十分離れること."""
        rackets = [
            # (name, w_bot, w_top, tri_h, throat_thick, max_shoulder_thick)
            ("Wilson CLASH 26 V3.0", 35.0, 121.0, 99.0, 24.0, 24.0),
            ("HEAD EXTREME MP 2026", 41.0, 130.0, 99.0, 21.5, 26.0),
        ]
        u_mid = CRADLE_INNER_BACK_U + CRADLE_GROOVE_DEPTH / 2.0

        for name, w_bot, w_top, tri_h, t_throat, t_max in rackets:
            with self.subTest(racket=name):
                half_slope = (w_top - w_bot) / (2.0 * tri_h)
                half_angle_deg = math.degrees(math.atan(half_slope))

                def make_racket_at(v_tri_bot: float):
                    shaft_len = 110.0
                    shaft_w = 13.5
                    parts = []
                    for sgn in (-1.0, 1.0):
                        x_mid = sgn * (w_bot / 2.0 + half_slope * (tri_h / 2.0) - shaft_w / 2.0)
                        v_mid = v_tri_bot + tri_h / 2.0
                        arm = (
                            Pos(x_mid, _u_to_y(u_mid), _v_to_z(v_mid))
                            * Rot(0, sgn * half_angle_deg, 0)
                            * Box(shaft_w, t_throat, shaft_len)
                        )
                        parts.append(arm)
                    bridge = Pos(
                        0.0,
                        _u_to_y(u_mid),
                        _v_to_z(v_tri_bot + tri_h + 6.0),
                    ) * Box(w_top - 10.0, t_max, 12.0)
                    handle = Pos(
                        0.0,
                        _u_to_y(u_mid),
                        _v_to_z(v_tri_bot - 45.0),
                    ) * Box(29.0, t_throat, 90.0)
                    return parts[0] + parts[1] + bridge + handle

                # 上方 (v_tri_bot = +10mm) では干渉ゼロ
                self.assertAlmostEqual(
                    _intersection_volume(self.holder, make_racket_at(10.0)),
                    0.0,
                    places=2,
                    msg=f"{name} must enter openly from above",
                )

                # 下へ降ろしていき着座高さ v_seat を二分探索で特定
                v_hi, v_lo = 10.0, -45.0
                self.assertGreater(
                    _intersection_volume(self.holder, make_racket_at(v_lo)),
                    5.0,
                    f"{name} must be caught by V-cradle before passing through",
                )
                for _ in range(18):
                    v_m = 0.5 * (v_hi + v_lo)
                    if _intersection_volume(self.holder, make_racket_at(v_m)) > 0.05:
                        v_lo = v_m
                    else:
                        v_hi = v_m

                v_seat = v_hi
                self.assertGreater(
                    v_seat + tri_h,
                    HOLDER_TOP_V + 15.0,
                    f"{name} throat bridge must stay well above cradle top",
                )
                # 最大フレーム厚26.0mm部でも棚板前面(u=0)および丸パイプ前端(u=+9.2)より十分手前にあること
                racket_backmost_u = u_mid - t_max / 2.0
                self.assertGreaterEqual(
                    racket_backmost_u,
                    PIPE_CENTER_U + PIPE_DIA / 2.0 + 8.0,
                    f"{name} max beam must clear both shelf and front pipe by >= 8.0mm",
                )
                self.assertLessEqual(
                    u_mid + t_throat / 2.0,
                    CRADLE_INNER_BACK_U + CRADLE_GROOVE_DEPTH - 1.0,
                )

    def test_06_support_free_overhangs_and_step_export_roundtrip(self) -> None:
        """Z>0.15mm にサポートやブリッジを必要とする急な下向き面が存在せず、STEP出力が正常に行えること."""
        for name, part in (("holder", self.holder), ("fit_test", self.fit_test)):
            for face in part.faces():
                cz = face.center().Z
                if cz <= 0.15:
                    continue
                n = face.normal_at(face.center())
                # ビルドプレート向きの急オーバーハング (normal.Z < -0.73 => 46.9°超) が存在しないこと
                if n.Z < -0.73:
                    self.assertLess(
                        face.area,
                        2.0,
                        f"{name} has unsupported downward overhang face at Z={cz:.2f}mm (area={face.area:.1f}mm^2, nZ={n.Z:.2f})",
                    )

        with tempfile.TemporaryDirectory() as tmpdir:
            main_path, fit_path = export_models(Path(tmpdir))
            self.assertTrue(main_path.exists())
            self.assertTrue(fit_path.exists())
            self.assertGreater(main_path.stat().st_size, 5000)
            self.assertGreater(fit_path.stat().st_size, 2000)

            imported_main = import_step(str(main_path))
            imported_fit = import_step(str(fit_path))
            self.assertEqual(len(imported_main.solids()), 1)
            self.assertEqual(len(imported_fit.solids()), 1)

    def test_07_racket_contact_fillets_and_fit_test_orientation_cue(self) -> None:
        """クレードル長尺エッジに保護Rがあり、テストピース前後の高さ差で向きが一目瞭然であること."""
        curved_long_faces = [
            f
            for f in self.holder.faces()
            if f.geom_type in (GeomType.CYLINDER, GeomType.TORUS, GeomType.BSPLINE)
            and f.bounding_box().size.Z > 45.0
        ]
        self.assertGreaterEqual(
            len(curved_long_faces),
            12,
            "V-cradle inner/outer sloped rails must be filleted to protect racket paint and hands",
        )

        # テストピースの前側 (Y > 0) は Z = FIT_TEST_HEIGHT (28.80mm) まで立ち上がり、
        # 棚板裏に入る後ろ側 (Y < -5mm) は Z < 24.5mm に低く抑えられて前後が視覚的に即判別できること
        front_half = self.fit_test & (Pos(0.0, 20.0, 50.0) * Box(80.0, 40.0, 100.0))
        rear_half = self.fit_test & (Pos(0.0, -25.0, 50.0) * Box(80.0, 40.0, 100.0))
        self.assertAlmostEqual(front_half.bounding_box().max.Z, FIT_TEST_HEIGHT, places=2)
        self.assertLess(rear_half.bounding_box().max.Z, FIT_TEST_HEIGHT - 4.5)


if __name__ == "__main__":
    unittest.main()
