"""ピクチャーレール用 HomePod mini 2 機械ロック式スタンドの自動幾何・干渉・カムロック・STEP出力検証テスト."""

from pathlib import Path
import math
import tempfile
import unittest
import numpy as np
from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Cylinder,
    Locations,
    Plane,
    Pos,
    RegularPolygon,
    Rot,
    Sphere,
    extrude,
    import_step,
)

from picture_rail_homepod_mini_stand.picture_rail_homepod_mini_stand import (
    BOLT_Z_POSITIONS,
    CABLE_CLIP_BORE_DIA,
    CABLE_CLIP_CENTER_U,
    CABLE_CLIP_CENTER_V,
    CABLE_CLIP_SLIT_GAP,
    CLAMP_FRONT_U,
    CLAMP_TOP_V,
    DECK_BOTTOM_V,
    DECK_FRONT_U,
    DECK_MIN_TOP_V,
    DECK_TILT_FORWARD_U_DEG,
    DECK_TILT_ROOM_CENTER_Z_DEG,
    FIT_TEST_WIDTH,
    FIT_U_OFFSET,
    FIT_V_OFFSET,
    HOMEPOD_FOOT_DIA,
    HOMEPOD_HEIGHT,
    HOMEPOD_SPHERE_DIA,
    M3_AXIS_V,
    M3_CBORE_DEPTH,
    MAIN_U_OFFSET,
    MAIN_V_OFFSET,
    POCKET_CENTER_U,
    POCKET_DEPTH,
    POCKET_FLOOR_DIA,
    RAIL_DEPTH,
    RAIL_HEIGHT,
    RAIL_INNER_DEPTH,
    RAIL_UNDER_LEDGE_DEPTH,
    SPINE_FRONT_U,
    STAND_WIDTH,
    T_ANCHOR_BOSS_HEIGHT,
    T_ANCHOR_SLOT_WIDTH,
    T_ANCHOR_TOTAL_HEIGHT,
    T_ANCHOR_WING_THICKNESS,
    build_fit_test_clamp,
    build_fit_test_kit,
    build_print_plate,
    build_stand,
    build_t_anchor,
    export_models,
    get_tilted_deck_plane,
)


class TestPictureRailHomePodMiniStand(unittest.TestCase):
    """ピクチャーレール用 HomePod mini 2 スタンド一式の幾何・物理制約テスト."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.stand = build_stand()
        cls.t_anchor = build_t_anchor()
        cls.fit_clamp = build_fit_test_clamp()
        cls.print_plate = build_print_plate()
        cls.fit_kit = build_fit_test_kit()

    def test_individual_parts_are_single_valid_closed_solids(self) -> None:
        """L字本体・カムTアンカー・テストクランプがそれぞれ単一閉ソリッドであること."""
        for name, part, min_vol in [
            ("stand", self.stand, 70_000.0),
            ("t_anchor", self.t_anchor, 300.0),
            ("fit_clamp", self.fit_clamp, 3_000.0),
        ]:
            solids = part.solids()
            self.assertEqual(len(solids), 1, f"{name} が単一ソリッドではありません")
            self.assertTrue(part.is_valid, f"{name} が不正なジオメトリです")
            self.assertGreater(part.volume, min_vol, f"{name} の体積が小さすぎます")

        self.assertEqual(len(self.print_plate.solids()), 3)
        self.assertEqual(len(self.fit_kit.solids()), 2)

        # プレート上の複数パーツ同士が一切干渉していないこと
        plate_solids = list(self.print_plate.solids())
        for i in range(len(plate_solids)):
            for j in range(i + 1, len(plate_solids)):
                inter = plate_solids[i] & plate_solids[j]
                vol = inter.volume if (inter is not None and inter.solids()) else 0.0
                self.assertLess(vol, 1e-4, f"造形プレート上のパーツ {i} と {j} が干渉しています")

    def test_print_orientation_and_bounding_boxes(self) -> None:
        """全パーツが Z=0 に完全接地し、設計外寸およびサポートフリー造形条件を満たすこと."""
        bb = self.stand.bounding_box()
        self.assertAlmostEqual(bb.min.Z, 0.0, places=3)
        self.assertAlmostEqual(bb.max.Z, STAND_WIDTH, places=3)
        self.assertAlmostEqual(bb.size.X, DECK_FRONT_U + RAIL_DEPTH, places=2)
        self.assertAlmostEqual((bb.min.X + bb.max.X) / 2.0, 0.0, places=2)
        self.assertAlmostEqual((bb.min.Y + bb.max.Y) / 2.0, 0.0, places=2)

        abb = self.t_anchor.bounding_box()
        self.assertAlmostEqual(abb.min.Z, 0.0, places=3)
        self.assertAlmostEqual(abb.max.Z, T_ANCHOR_TOTAL_HEIGHT, places=3)

        pbb = self.print_plate.bounding_box()
        self.assertAlmostEqual(pbb.min.Z, 0.0, places=3)
        self.assertAlmostEqual(pbb.max.Z, STAND_WIDTH, places=3)

        fbb = self.fit_clamp.bounding_box()
        self.assertAlmostEqual(fbb.min.Z, 0.0, places=3)
        self.assertAlmostEqual(fbb.max.Z, FIT_TEST_WIDTH, places=3)

    def test_picture_rail_wall_and_sub_beam_zero_interference(self) -> None:
        """ピクチャーレール外寸・背面壁・上方小梁と干渉ゼロであり、二点接地と下面受けが機能すること."""
        # 造形時は左壁(ケーブルクリップ)側を Z=0 接地とするため Y軸周り180°回転座標: X = -(u + MAIN_U_OFFSET), Y = v + MAIN_V_OFFSET
        x_off = MAIN_U_OFFSET
        y_off = MAIN_V_OFFSET

        def bx(u_center: float) -> float:
            return -(u_center + x_off)

        # 1. 壁面領域 (u <= -14.60)
        wall_box = Pos(bx(-RAIL_DEPTH - 20.0), -40.0 + y_off, STAND_WIDTH / 2.0) * Box(
            40.0, 220.0, STAND_WIDTH + 10.0
        )
        # 2. 小梁領域 (v >= +20.30, u = -14.60 .. +75.00)
        beam_box = Pos(bx(30.0), RAIL_HEIGHT + 20.0 + y_off, STAND_WIDTH / 2.0) * Box(
            100.0, 40.0, STAND_WIDTH + 10.0
        )
        # 3. ピクチャーレール外寸 (u = -14.60 .. 0.00, v = 0.00 .. +20.30)
        rail_box = Pos(
            bx(-RAIL_DEPTH / 2.0), RAIL_HEIGHT / 2.0 + y_off, STAND_WIDTH / 2.0
        ) * Box(RAIL_DEPTH, RAIL_HEIGHT, STAND_WIDTH + 10.0)

        for label, obstacle in [("壁面", wall_box), ("上方小梁", beam_box), ("レール外寸", rail_box)]:
            inter = self.stand & obstacle
            vol = inter.volume if (inter is not None and inter.solids()) else 0.0
            self.assertLess(vol, 1e-3, f"本体が {label} と干渉しています (vol={vol})")

        # 4. レール前面 (u=0..+0.4)・レール下面受け (v=-0.4..0)・下部壁当てヒール (u=-14.6..-14.2) の密着確認
        front_probe = Pos(bx(0.2), 15.0 + y_off, STAND_WIDTH / 2.0) * Box(0.4, 3.0, 20.0)
        under_probe = Pos(
            bx(-RAIL_UNDER_LEDGE_DEPTH / 2.0), -0.2 + y_off, STAND_WIDTH / 2.0
        ) * Box(RAIL_UNDER_LEDGE_DEPTH - 2.0, 0.4, 20.0)
        heel_probe = Pos(bx(-RAIL_DEPTH + 0.2), -95.0 + y_off, STAND_WIDTH / 2.0) * Box(
            0.4, 15.0, 20.0
        )
        for label, probe in [
            ("レール前面座", front_probe),
            ("レール下面受け段差", under_probe),
            ("下部壁当てヒール", heel_probe),
        ]:
            self.assertGreater((self.stand & probe).volume, 1.0, f"{label} が接触していません")

        # 5. 中間背面リリーフ (壁紙不陸逃げ u = -14.60 .. -14.10, v = -45.0) が空いていること
        mid_relief_probe = Pos(bx(-RAIL_DEPTH + 0.25), -45.0 + y_off, STAND_WIDTH / 2.0) * Box(
            0.5, 20.0, 20.0
        )
        mid_inter = self.stand & mid_relief_probe
        mid_vol = mid_inter.volume if (mid_inter is not None and mid_inter.solids()) else 0.0
        self.assertLess(mid_vol, 1e-3, "背面スパイン中間の壁紙不陸逃げが形成されていません")

    def test_clamp_neck_minimum_structural_thickness(self) -> None:
        """クランプ〜垂直スパイン首元の最小肉厚が約9mm以上確保され、くびれ弱点が存在しないこと."""
        probe_radius = 4.30  # 直径 8.60mm の連続ソリッド円柱が首元全域に100%内包されること
        neck_load_path_uv = [
            (5.40, 1.00),    # クランプ下部 (M3ザグリ下端 v=+6.85 より下)
            (5.20, -3.50),   # レール角 (0,0) 斜め手前下の首元中央
            (1.00, -6.50),   # レール下面受け直下〜ガセット中央
            (-5.00, -6.00),  # 垂直スパイン上部肩口
        ]
        for model_name, part, u_off, v_off, z_span in [
            ("stand", self.stand, MAIN_U_OFFSET, MAIN_V_OFFSET, STAND_WIDTH - 4.0),
            ("fit_clamp", self.fit_clamp, FIT_U_OFFSET, FIT_V_OFFSET, FIT_TEST_WIDTH - 2.0),
        ]:
            z_center = (STAND_WIDTH if model_name == "stand" else FIT_TEST_WIDTH) / 2.0
            for u_c, v_c in neck_load_path_uv:
                px = -(u_c + u_off)
                py = v_c + v_off
                cyl = Pos(px, py, z_center) * Cylinder(
                    radius=probe_radius, height=z_span
                )
                inter = part & cyl
                vol = inter.volume if (inter is not None and inter.solids()) else 0.0
                self.assertAlmostEqual(
                    vol,
                    cyl.volume,
                    delta=cyl.volume * 0.01,
                    msg=(
                        f"{model_name} の首元 (u={u_c}, v={v_c}) の肉厚が不足しています "
                        f"(内包率 {vol / cyl.volume * 100:.1f}% < 99%)"
                    ),
                )

    def test_cam_t_anchor_slot_insertion_auto_stop_and_wall_screw_clearance(self) -> None:
        """カムTアンカーの7.5mm溝通過・自動回転ストップ・M3ナット保持・内部ビス頭非干渉を検証."""
        # Tアンカーはローカル原点中心、Z = 0(ウイング背面・ナット側) .. 6.60(円筒ボス先端)、挿入時 Y 幅 = 7.20mm
        # 1. 水平姿勢 (0°) で開口 7.50mm の上下リップ間を無干渉で通過できること
        slot_gap = 7.50
        upper_lip = Pos(0.0, slot_gap / 2.0 + 5.0, T_ANCHOR_TOTAL_HEIGHT / 2.0) * Box(
            30.0, 10.0, T_ANCHOR_TOTAL_HEIGHT + 4.0
        )
        lower_lip = Pos(0.0, -(slot_gap / 2.0 + 5.0), T_ANCHOR_TOTAL_HEIGHT / 2.0) * Box(
            30.0, 10.0, T_ANCHOR_TOTAL_HEIGHT + 4.0
        )
        for lip in (upper_lip, lower_lip):
            inter = self.t_anchor & lip
            self.assertLess(inter.volume if (inter is not None and inter.solids()) else 0.0, 1e-3)

        # 2. 右回し締結時の回転検証:
        #    実機装着時はボス先端 (local Z=6.60) がレール正面 (+u) を向き、ナット背面 (local Z=0.0) が奥壁 (-u) を向く。
        #    正面から M3 ボルトを右回しすると回転ベクトルは -u (= local -Z) となるため Rot(0, 0, -deg) で回転する。
        min_cav_h = 15.60
        min_cav_walls = Pos(0.0, min_cav_h / 2.0 + 5.0, T_ANCHOR_TOTAL_HEIGHT / 2.0) * Box(
            30.0, 10.0, 20.0
        ) + Pos(0.0, -(min_cav_h / 2.0 + 5.0), T_ANCHOR_TOTAL_HEIGHT / 2.0) * Box(
            30.0, 10.0, 20.0
        )
        for deg in (0.0, 25.0, 45.0, 65.0):
            rotated = Rot(0, 0, -deg) * self.t_anchor
            inter = rotated & min_cav_walls
            vol = inter.volume if (inter is not None and inter.solids()) else 0.0
            self.assertLess(
                vol, 1e-3, f"右回し {deg}° で最小キャビティ({min_cav_h}mm)に引っ掛かっています"
            )

        max_cav_h = 17.00
        max_cav_walls = Pos(0.0, max_cav_h / 2.0 + 5.0, T_ANCHOR_TOTAL_HEIGHT / 2.0) * Box(
            30.0, 10.0, 20.0
        ) + Pos(0.0, -(max_cav_h / 2.0 + 5.0), T_ANCHOR_TOTAL_HEIGHT / 2.0) * Box(
            30.0, 10.0, 20.0
        )
        rotated_90 = Rot(0, 0, -90.0) * self.t_anchor
        stop_inter = rotated_90 & max_cav_walls
        stop_vol = stop_inter.volume if (stop_inter is not None and stop_inter.solids()) else 0.0
        self.assertGreater(
            stop_vol,
            0.5,
            f"最大キャビティ({max_cav_h}mm)で90°位置のカムストッパーが内壁に届いていません",
        )

        # 3. ロック姿勢 (-78°) で上下リップ裏 (|Y| >= 3.9mm) に各 3.2mm 以上しっかり掛かること
        locked = Rot(0, 0, -78.0) * self.t_anchor
        lbb = locked.bounding_box()
        self.assertGreaterEqual(lbb.max.Y, 3.9 + 3.2)
        self.assertLessEqual(lbb.min.Y, -(3.9 + 3.2))

        # 4. Z=0 に広い Tウイング面が全面接地していること (浮きウイングオーバーハング防止)
        z0_probe = Pos(0.0, 0.0, 0.15) * Box(16.0, 6.8, 0.3)
        self.assertGreater((self.t_anchor & z0_probe).volume, 18.0, "TアンカーのウイングがZ=0に接地していません")

        # 5. M3六角ナット (二面幅 5.50mm, 厚み 2.40mm) が Z=0 側の背面ポケットに無干渉で収まり空回りしないこと
        circum_r = (5.50 / 2.0) / math.cos(math.radians(30.0))
        with BuildPart() as nut_bp:
            with BuildSketch(Plane.XY.offset(0.20)):
                RegularPolygon(radius=circum_r, side_count=6)
            extrude(amount=2.40)
        nut_inter = self.t_anchor & nut_bp.part
        self.assertLess(
            nut_inter.volume if (nut_inter is not None and nut_inter.solids()) else 0.0, 1e-3
        )
        spun_nut = Rot(0, 0, 30.0) * nut_bp.part
        self.assertGreater((self.t_anchor & spun_nut).volume, 1.0, "M3六角ナットの回り止めが効いていません")

        # 6. 実機締結時 (前リップ厚 2.0mm -> ウイング前面 u=-2.0mm -> Tアンカー後端 u=-7.0mm、
        #    M3×12mm ボルト座面 u=+5.20mm -> 先端 u=-6.80mm) に、奥壁(u=-12.6mm)の鍋ビス頭(u<=-9.8mm)まで3mm近い余裕があること
        lip_thickness = 2.00
        t_anchor_rear_u = -(lip_thickness + T_ANCHOR_WING_THICKNESS)
        bolt_seat_u = CLAMP_FRONT_U - M3_CBORE_DEPTH
        bolt_tip_u = bolt_seat_u - 12.00
        wall_screw_front_u = -RAIL_INNER_DEPTH + 2.80  # -9.80mm (高さ2.8mmの余裕見た鍋ビス頭)
        self.assertGreater(t_anchor_rear_u - wall_screw_front_u, 2.50)
        self.assertGreater(bolt_tip_u - wall_screw_front_u, 2.50)
        self.assertGreaterEqual(bolt_tip_u, t_anchor_rear_u)  # Tアンカー背面から突き出さない

    def test_tilted_deck_pocket_homepod_sphere_and_cable_clip(self) -> None:
        """ケーブルロックZ=0完全接地・2軸傾斜順テーパー・浅溝・M3涙滴+Z向き・球体非干渉を検証."""
        x_off = MAIN_U_OFFSET
        y_off = MAIN_V_OFFSET

        def bx(u_center: float) -> float:
            return -(u_center + x_off)

        deck_plane = get_tilted_deck_plane(u_offset=x_off, v_offset=y_off)
        n = deck_plane.z_dir
        self.assertGreater(n.Y, 0.98)
        self.assertLess(n.X, -0.12)    # +u (= -X方向: 手前) へ 7.5° 傾斜
        self.assertGreater(n.Z, 0.03)  # +Z方向 (= 部屋中央側・造形上向き順テーパー) へ 2.5° 傾斜

        # 浅溝の中央が空洞 (深さ 1.80mm) であり、その直下に十分なソリッド反射床があること
        with BuildPart() as air_bp:
            with BuildSketch(deck_plane.offset(-POCKET_DEPTH + 0.25)):
                Locations((0, 0))
                RegularPolygon(radius=POCKET_FLOOR_DIA / 2.0 - 2.0, side_count=24)
            extrude(amount=POCKET_DEPTH + 1.0)
        air_inter = self.stand & air_bp.part
        self.assertLess(
            air_inter.volume if (air_inter is not None and air_inter.solids()) else 0.0,
            1e-2,
            "天板のシリコン足浅溝が所定深さまで彫られていません",
        )

        with BuildPart() as floor_bp:
            with BuildSketch(deck_plane.offset(-POCKET_DEPTH - 8.0)):
                RegularPolygon(radius=16.0, side_count=24)
            extrude(amount=7.5)
        self.assertAlmostEqual(
            (self.stand & floor_bp.part).volume, floor_bp.part.volume, delta=5.0
        )

        # HomePod mini 2 実寸截頭球モデル (底面〜天面高さ 84.3mm、赤道最大直径 97.9mm) の3D非干渉検証
        sphere_center = deck_plane.origin + deck_plane.z_dir * (HOMEPOD_HEIGHT / 2.0)
        raw_sphere = Pos(sphere_center.X, sphere_center.Y, sphere_center.Z) * Sphere(
            radius=HOMEPOD_SPHERE_DIA / 2.0
        )
        with BuildPart() as height_slab_bp:
            with BuildSketch(deck_plane):
                RegularPolygon(radius=80.0, side_count=32)
            extrude(amount=HOMEPOD_HEIGHT)
        hp_sphere = raw_sphere & height_slab_bp.part

        # 1) 背面スパイン (u <= SPINE_FRONT_U) から 7.5mm 手前に膨らませた境界ボックスとも非干渉であること
        spine_clearance_box = Pos(
            bx(SPINE_FRONT_U + 7.5 - 20.0), -45.0 + y_off, STAND_WIDTH / 2.0
        ) * Box(40.0, 90.0, STAND_WIDTH + 40.0)
        sp_inter = hp_sphere & spine_clearance_box
        self.assertLess(
            sp_inter.volume if (sp_inter is not None and sp_inter.solids()) else 0.0,
            1e-2,
            "HomePod mini 2 球体背面とスパインの音響クリアランスが 7.5mm 未満です",
        )

        # 2) 上方小梁 (v >= RAIL_HEIGHT) から下へ 24mm 下げた安全面とも非干渉であること (実クリアランス約27〜30mm)
        beam_clearance_box = Pos(
            bx(40.0), RAIL_HEIGHT - 24.0 + 25.0 + y_off, STAND_WIDTH / 2.0
        ) * Box(120.0, 50.0, STAND_WIDTH + 40.0)
        bm_inter = hp_sphere & beam_clearance_box
        self.assertLess(
            bm_inter.volume if (bm_inter is not None and bm_inter.solids()) else 0.0,
            1e-2,
            "HomePod mini 2 天面と小梁下端のクリアランスが 24mm 未満です",
        )

        # 3) M3ボルト2本の正面ストレートドライバー動線 + ティアドロップ屋根が +Z (造形上向き) を向いていること
        for bz_raw in BOLT_Z_POSITIONS:
            bz = STAND_WIDTH - bz_raw
            driver = (
                Pos(bx(100.0), M3_AXIS_V + y_off, bz)
                * Rot(0, 90, 0)
                * Cylinder(radius=3.0, height=190.0)
            )
            dr_inter = hp_sphere & driver
            self.assertLess(
                dr_inter.volume if (dr_inter is not None and dr_inter.solids()) else 0.0,
                1e-2,
                f"Z={bz} のM3ボルト正面ドライバー動線がHomePod球体と干渉しています",
            )
            # ボルト穴貫通確認
            shank_probe = (
                Pos(bx(CLAMP_FRONT_U / 2.0), M3_AXIS_V + y_off, bz)
                * Rot(0, 90, 0)
                * Cylinder(radius=1.45, height=CLAMP_FRONT_U + 2.0)
            )
            sh_inter = self.stand & shank_probe
            self.assertLess(
                sh_inter.volume if (sh_inter is not None and sh_inter.solids()) else 0.0, 1e-2
            )
            # ザグリ穴のティアドロップ頂点が +Z 側 (bz + 3.85mm) に開いており、逆側 (-Z: bz - 3.85mm) はソリッドであること
            cb_x = bx(CLAMP_FRONT_U - M3_CBORE_DEPTH / 2.0)
            top_apex_probe = Pos(cb_x, M3_AXIS_V + y_off, bz + 3.85) * Box(1.0, 0.4, 0.4)
            bot_solid_probe = Pos(cb_x, M3_AXIS_V + y_off, bz - 3.85) * Box(1.0, 0.4, 0.4)
            top_inter = self.stand & top_apex_probe
            self.assertLess(
                top_inter.volume if (top_inter is not None and top_inter.solids()) else 0.0,
                1e-3,
                "M3ザグリ穴のティアドロップ垂れ防止屋根が +Z (上側) を向いていません",
            )
            self.assertGreater(
                (self.stand & bot_solid_probe).volume,
                0.10,
                "M3ザグリ穴のティアドロップが逆さま (-Z下向き) になっています",
            )

        # 4) 電源コードクリップが Z = 0.0 .. 10.0mm (ビルドプレート直置き!) に配置され、開通・接地していること
        clip_z0_contact = Pos(
            bx(CABLE_CLIP_CENTER_U - 3.4), CABLE_CLIP_CENTER_V + y_off, 0.25
        ) * Box(1.2, 2.0, 0.5)
        self.assertGreater(
            (self.stand & clip_z0_contact).volume,
            0.8,
            "電源コードクリップが Z=0 ビルドプレート面にベタ置き接地していません",
        )

        clip_bore_probe = Pos(
            bx(CABLE_CLIP_CENTER_U), CABLE_CLIP_CENTER_V + y_off, 5.0
        ) * Cylinder(radius=CABLE_CLIP_BORE_DIA / 2.0 - 0.15, height=9.0)
        cb_inter = self.stand & clip_bore_probe
        self.assertLess(
            cb_inter.volume if (cb_inter is not None and cb_inter.solids()) else 0.0, 1e-2
        )

        clip_slit_probe = Pos(
            bx(CABLE_CLIP_CENTER_U),
            CABLE_CLIP_CENTER_V - 3.0 + y_off,
            5.0,
        ) * Box(CABLE_CLIP_SLIT_GAP - 0.25, 4.0, 9.0)
        cs_inter = self.stand & clip_slit_probe
        self.assertLess(
            cs_inter.volume if (cs_inter is not None and cs_inter.solids()) else 0.0, 1e-2
        )

        # 5) Z=0 接地面積が 3,000mm^2 超であり、Z>0 の下向きオーバーハング面 (>45.1°) が完全ゼロであること
        verts, tris = self.stand.tessellate(tolerance=0.05)
        v = np.array([[p.X, p.Y, p.Z] for p in verts])
        t = np.array(tris)
        p0, p1, p2 = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
        cross = np.cross(p1 - p0, p2 - p0)
        areas = 0.5 * np.linalg.norm(cross, axis=1)
        valid = areas > 1e-9
        normals = cross[valid] / (2.0 * areas[valid, None])
        areas = areas[valid]
        centers = (p0[valid] + p1[valid] + p2[valid]) / 3.0

        z0_bed_area = float(areas[(normals[:, 2] < -0.99) & (np.abs(centers[:, 2]) < 0.05)].sum())
        self.assertGreater(z0_bed_area, 3000.0, f"Z=0 接地面積が想定より小さいです ({z0_bed_area:.1f} mm^2)")

        down = (normals[:, 2] < -1e-4) & (centers[:, 2] > 0.2)
        if np.any(down):
            deg_from_vert = np.degrees(np.arccos(np.clip(-normals[down, 2], 0.0, 1.0)))
            steep_area = float(areas[down][deg_from_vert < 44.5].sum())
            self.assertLess(
                steep_area,
                0.5,
                f"45°を超える下向きオーバーハング面が存在します (area={steep_area:.2f} mm^2)",
            )

    def test_fit_test_kit_and_step_export_roundtrip(self) -> None:
        """本番プレートと事前嵌合テストキットのSTEP出力・再読込体積一致を検証."""
        with tempfile.TemporaryDirectory() as tmpdir:
            main_step, fit_step = export_models(Path(tmpdir))
            self.assertTrue(main_step.exists())
            self.assertTrue(fit_step.exists())

            reloaded_main = import_step(str(main_step))
            reloaded_fit = import_step(str(fit_step))

            self.assertEqual(len(reloaded_main.solids()), 3)
            self.assertEqual(len(reloaded_fit.solids()), 2)
            self.assertAlmostEqual(
                reloaded_main.volume, self.print_plate.volume, delta=self.print_plate.volume * 0.002
            )
            self.assertAlmostEqual(
                reloaded_fit.volume, self.fit_kit.volume, delta=self.fit_kit.volume * 0.002
            )


if __name__ == "__main__":
    unittest.main()
