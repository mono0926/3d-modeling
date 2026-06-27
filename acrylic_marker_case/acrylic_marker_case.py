import cadquery as cq
import os

"""
設計要件:
    - 13mm径、長さ151mmのアクリルマーカーを収納。
    - パレット（色見本用窪み）と色番号のテキスト（高さ0.6mm）を両端に配置。
    - 中央にPETG向けの適度なしなりを持たせたスナップフィット（Cクリップ）を配置。
    - 2つのケースを重ねて携帯ケースになる（スタッキング設計）。
    - 各ケース（1と2）とテスト用（1本分）のアセンブリとしてSTEPを生成。
    - Bambu Studioでマルチパーツとして認識され、文字のみを黒に設定可能。

推奨フィラメント:
    - ベース: PLA/PETG 白色系
    - テキスト部分: PLA/PETG 黒色等 (AMSで割り当て)

推奨スライサー設定 (Bambu Studio):
    - ウォールジェネレーター: Arachne
    - アイロニング: 「最上層のみ (Topmost surface only)」推奨

磁石の接着について（重要）:
    - 重ねた時に反発しないよう、片側（例えば左側2箇所）はN極を上に、反対側（右側2箇所）はS極を上にして接着してください。
    - こうすることで、同じケースをひっくり返して重ねた際に必ずNとSが合わさります。

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# --- Parameters ---
PEN_D = 13.0
PEN_L = 151.0
PITCH = 18.0

PEN_CLEARANCE = 0.6
GROOVE_D = PEN_D + PEN_CLEARANCE

CLIP_D = 13.1  
CLIP_OPENING = 12.0
SNAP_L = 12.0
CLIP_BLOCK_W = 16.0  

BASE_T = 2.5
GROOVE_H = 3.5
WALL_Z = 16.5
WALL_T = 7.0

PALETTE_L = 16.0
CLEARANCE_L = 2.0
TOTAL_PEN_L = PEN_L + CLEARANCE_L
INNER_L = TOTAL_PEN_L + 2 * PALETTE_L
TOTAL_L = INNER_L + 2 * WALL_T

GROOVE_TOP_Z = BASE_T + GROOVE_H
PEN_Z = BASE_T + GROOVE_D / 2.0
CLIP_BLOCK_H = PEN_Z + 4.0 - GROOVE_TOP_Z

TEXT_HEIGHT = 0.6
FONT_SIZE = 4.0

# 出力するケースのバリエーション
CASES = {
    "1": [("47", "20"), ("30", "50"), ("63", "129"), ("23", "45"), ("25", "145"), ("10", "43")],
    "2": [("27", "158"), ("48", "29"), ("36", "46"), ("38", "39"), ("99", "35"), ("132", "64")],
    "test": [("47", "20")]
}

def create_case(pen_numbers):
    n_pens = len(pen_numbers)
    inner_w = n_pens * PITCH
    total_w = inner_w + 2 * WALL_T

    # 1. 外形ベース
    sk = cq.Sketch().rect(total_w, TOTAL_L).vertices().fillet(4.0)
    body = cq.Workplane("XY").placeSketch(sk).extrude(WALL_Z)

    # 2. 内側のくり抜き（壁の形成）
    inner_sk = cq.Sketch().rect(inner_w, INNER_L).vertices().fillet(2.0)
    pocket = cq.Workplane("XY", origin=(0, 0, GROOVE_TOP_Z)).placeSketch(inner_sk).extrude(WALL_Z - GROOVE_TOP_Z)
    body = body.cut(pocket)

    xs = [(i - (n_pens - 1) / 2.0) * PITCH for i in range(n_pens)]
    
    texts_compound = None

    for i, x in enumerate(xs):
        # クリップ用ブロックの追加
        clip_block = cq.Workplane("XY", origin=(x, 0, GROOVE_TOP_Z + CLIP_BLOCK_H/2)).box(CLIP_BLOCK_W, SNAP_L, CLIP_BLOCK_H)
        body = body.union(clip_block)
        
        # 中央クリップ部の円柱カット
        clip_cyl = cq.Workplane("XZ", origin=(x, 0, PEN_Z)).circle(CLIP_D / 2.0).extrude(TOTAL_PEN_L/2.0, both=True)
        body = body.cut(clip_cyl)
        
        # クリップ上部の開口部カット
        clip_slot = cq.Workplane("XY", origin=(x, 0, PEN_Z)).rect(CLIP_OPENING, SNAP_L).extrude(WALL_Z)
        body = body.cut(clip_slot)
        
        # クリップ挿入部の面取り（リードイン）
        lead_in = (
            cq.Workplane("XZ", origin=(x, 0, GROOVE_TOP_Z + CLIP_BLOCK_H - 1.5))
            .moveTo(-CLIP_OPENING/2.0, 0)
            .lineTo(-14.0/2.0, 1.5)
            .lineTo(14.0/2.0, 1.5)
            .lineTo(CLIP_OPENING/2.0, 0)
            .close()
            .extrude(SNAP_L/2.0, both=True)
        )
        body = body.cut(lead_in)
        
        # クリップ部以外の緩い溝のカット
        y_start = SNAP_L / 2.0
        y_end = TOTAL_PEN_L / 2.0
        y_len = y_end - y_start
        y_center = y_start + y_len / 2.0
        
        # Yプラス側
        loose_cyl_1 = cq.Workplane("XZ", origin=(x, y_center, PEN_Z)).circle(GROOVE_D / 2.0).extrude(y_len / 2.0, both=True)
        loose_slot_1 = cq.Workplane("XY", origin=(x, y_center, PEN_Z)).rect(GROOVE_D, y_len).extrude(WALL_Z)
        body = body.cut(loose_cyl_1).cut(loose_slot_1)
        
        # Yマイナス側
        loose_cyl_2 = cq.Workplane("XZ", origin=(x, -y_center, PEN_Z)).circle(GROOVE_D / 2.0).extrude(y_len / 2.0, both=True)
        loose_slot_2 = cq.Workplane("XY", origin=(x, -y_center, PEN_Z)).rect(GROOVE_D, y_len).extrude(WALL_Z)
        body = body.cut(loose_cyl_2).cut(loose_slot_2)
        
        # パレット窪みとテキストの配置
        num_plus, num_minus = pen_numbers[i]
        
        for sign in [1, -1]:
            # 丸いパレット窪み
            cy = sign * (TOTAL_PEN_L / 2.0 + 6.0)
            palette = cq.Workplane("XY", origin=(x, cy, GROOVE_TOP_Z)).circle(4.5).extrude(-1.0)
            body = body.cut(palette)
            
            # 色番号テキスト (四角い窪みを削除し、浮き出し文字に変更)
            ry = sign * (TOTAL_PEN_L / 2.0 + 13.0)
            text_str = num_plus if sign == 1 else num_minus
            
            t = cq.Workplane("XY").workplane(offset=GROOVE_TOP_Z).center(x, ry).text(
                txt=text_str,
                fontsize=FONT_SIZE,
                distance=TEXT_HEIGHT,
                halign="center",
                valign="center",
                font="Arial"
            )
            
            if texts_compound is None:
                texts_compound = t.val()
            else:
                texts_compound = texts_compound.fuse(t.val())

    # 4. マグネット穴と位置合わせピン
    MAGNET_D = 6.1
    MAGNET_H = 3.1

    hole_centers = [
        ( inner_w/2 + WALL_T/2,  INNER_L/2 + WALL_T/2),
        (-inner_w/2 - WALL_T/2,  INNER_L/2 + WALL_T/2),
        ( inner_w/2 + WALL_T/2, -INNER_L/2 - WALL_T/2),
        (-inner_w/2 - WALL_T/2, -INNER_L/2 - WALL_T/2),
    ]

    for hx, hy in hole_centers:
        magnet_hole = cq.Workplane("XY", origin=(hx, hy, WALL_Z)).circle(MAGNET_D/2.0).extrude(-MAGNET_H)
        body = body.cut(magnet_hole)

    # 位置合わせピン
    pin_y_offsets = [INNER_L / 4.0, -INNER_L / 4.0]
    for py in pin_y_offsets:
        # 左側の壁にピン
        pin = cq.Workplane("XY", origin=(-(inner_w/2 + WALL_T/2), py, WALL_Z)).circle(1.5).extrude(2.0)
        pin = pin.edges(">Z").chamfer(0.5)
        body = body.union(pin)
        
        # 右側の壁に穴
        hole = cq.Workplane("XY", origin=(inner_w/2 + WALL_T/2, py, WALL_Z)).circle(1.7).extrude(-2.5)
        body = body.cut(hole)

    # 5. 外周底面のフィレット (手触り向上)
    body = body.edges("<Z").fillet(1.5)

    # アセンブリの構成
    assy = cq.Assembly()
    assy.add(body, name="Base", color=cq.Color(0.9, 0.9, 0.9, 1.0))
    if texts_compound is not None:
        assy.add(texts_compound, name="Text", color=cq.Color(0.1, 0.1, 0.1, 1.0))

    return assy, total_w

# プレートの生成とエクスポート
out_dir = os.path.dirname(__file__)

try:
    from ocp_vscode import show
    has_ocp = True
except ImportError:
    has_ocp = False

main_assy = cq.Assembly()
current_x = 0.0

for case_name, pen_numbers in CASES.items():
    print(f"Generating Case {case_name}...")
    assy, total_w = create_case(pen_numbers)
    
    # AssemblyごとSTEPファイルに出力
    step_path = os.path.join(out_dir, f"acrylic_marker_case_{case_name}.step")
    assy.save(step_path, "STEP")
    print(f"Exported {step_path}")
    
    # プレビュー用にX方向にずらして配置
    main_assy.add(assy, loc=cq.Location(cq.Vector(current_x, 0, 0)), name=f"Case_{case_name}")
    current_x += total_w + 10.0

if has_ocp:
    show(main_assy)
