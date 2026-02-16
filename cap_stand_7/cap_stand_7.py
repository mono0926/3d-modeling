import cadquery as cq
import os
import math

"""
設計要件:
    - ペットボトルのキャップ（計7個、中心1、周囲6のヘキサゴン配置）を保持するスタンド。
    - 花瓶を逆さまにして乾燥させる用途のため、口を塞がず通気性を確保する。
    - 各ソケット底面に直径 15mm の通気穴を配置。
    - キャップの着脱がスムーズな Friction Fit（摩擦保持）を目指す。
    - 最新の3Dプリンター（Bambu Lab P2S 等）での出力を想定。
    - モデルごとに専用ディレクトリで管理し、STEPファイルを出力する。

推奨フィラメント:
    - PETG (耐水性があり、適度な柔軟性がキャップの保持と着脱に適しているため)
    - 表面が滑らかで化学耐性が高いため、付着して乾いた「ニス」の除去（剥離）が容易。
    - PLAでも代用可能だが、実用性とメンテナンス性（ニスの掃除）からPETGを推奨。

印刷統計（予想）:
    - cap_stand_7.step: 印刷時間 約45分、フィラメント使用量 約20g
    - cap_stand_test.step: 印刷時間 約10分、フィラメント使用量 約3g

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの `history.md` を参照。
"""

# --- Parameters ---
RECOMMENDED_FILAMENT = "PETG"  # 推奨材質: PETG (耐水・適度な弾性)

# 物理的な嵌め合い（Friction Fit）の調整
CAP_DIAMETER = 29.6       # キャップの実測外径 (Rev 11 で修正)
CLEARANCE = 0.1          # はめ合わせの余裕 (摩擦保持のため小さく設定)
SOCKET_WALL = 1.6        # 壁厚 (0.4mmノズル 4本分)
SOCKET_HEIGHT = 4.0      # ソケットの高さ
BASE_THICKNESS = 3.0     # ベースプレートの厚み
BASE_RADIUS = 50.0       # 六角ベースの外接円半径
HOLE_DIA = 15.0          # 通気穴の直径
CHAMFER = 0.6            # 上面エッジの面取り量
PITCH = 45.0             # キャップ中心間の距離 (干渉防止)

# --- Derived Design Constants ---
# ソケット内径 = キャップ径 + クリアランス
SOCKET_INNER_DIA = CAP_DIAMETER + CLEARANCE
# ソケット外径 = 内径 + 壁厚*2
SOCKET_OUTER_DIA = SOCKET_INNER_DIA + (SOCKET_WALL * 2)

# --- Coordinates Generation ---
# 中心(0,0) + 半径PITCHの正六角形の頂点6つ
coords = [(0, 0)]
for i in range(6):
    angle = math.radians(60 * i)
    x = PITCH * math.cos(angle)
    y = PITCH * math.sin(angle)
    coords.append((x, y))

# --- Modeling ---

def generate_stand():
    # 1. Base Structure
    # 全てのソケット位置に円柱を描き、それらをhullで囲んでベースプレート形状を作る予定だったが、
    # 実行環境でhullが使えないため、単純な六角形プレート＋フィレットで代用する
    # 六角形の「辺」の部分でもソケットがはみ出さないように、外接円半径を大きめに取る
    # 必要半径 = (PITCH + 半径) / cos(30度)
    REQ_DIST = PITCH + (SOCKET_OUTER_DIA / 2.0)
    BASE_RADIUS = REQ_DIST / math.cos(math.radians(30))

    base = (
        cq.Workplane("XY")
        .polygon(6, BASE_RADIUS * 2) # 対角距離（直径）を指定
        .extrude(BASE_THICKNESS)
        .edges("not #Z").fillet(5.0) # ルールに基づき堅牢なセレクターを使用
    )

    # 2. Add Sockets (Cylinders)
    # ベースの上にソケットの壁となる円柱を追加
    sockets = (
        cq.Workplane("XY")
        .workplane(offset=BASE_THICKNESS) # ベースの上面を作業平面に
        .pushPoints(coords)
        .circle(SOCKET_OUTER_DIA / 2.0)
        .extrude(SOCKET_HEIGHT)
    )

    # ベースとソケットを結合
    result = base.union(sockets)

    # 3. Make Holes (Socket Recess)
    # キャップが入る穴を開ける (上から、ソケットの深さ分)
    # これにより、底面はBASE_THICKNESSの高さで残る
    result = (
        result
        .faces(">Z").workplane()
        .pushPoints(coords)
        .hole(SOCKET_INNER_DIA, depth=SOCKET_HEIGHT)
    )

    # 4. Make Ventilation Holes (Through Base)
    # 底面の通気穴（ベースプレートを貫通）
    result = (
        result
        .faces("<Z").workplane() # 底面から
        .pushPoints(coords)
        .hole(HOLE_DIA) # 貫通
    )

    # 5. Finishing (Chamfer)
    # ソケットの入り口（上端の内側と外側）を面取りしてキャップを入れやすく、かつ手触りを良くする

    # 穴の縁（内側）
    result = (
        result
        .faces(">Z").edges() # 上面の全エッジ（内径円周＋外径円周）
        .chamfer(CHAMFER)
    )

    return result

def generate_test_piece():
    """
    サイズ確認用のテストピース (ソケット1個分)
    """
    # 1. Base Structure (Single Socket Base)
    # ソケット外径 + 余白 (5mm程度)
    TEST_BASE_DIA = SOCKET_OUTER_DIA + 5.0

    base = (
        cq.Workplane("XY")
        .circle(TEST_BASE_DIA / 2.0)
        .extrude(BASE_THICKNESS)
        # 底面エッジのフィレットは省略(テスト用なので)
    )

    # 2. Add Socket (Single)
    socket = (
        cq.Workplane("XY")
        .workplane(offset=BASE_THICKNESS)
        .circle(SOCKET_OUTER_DIA / 2.0)
        .extrude(SOCKET_HEIGHT)
    )

    result = base.union(socket)

    # 3. Make Hole (Socket Recess)
    result = (
        result
        .faces(">Z").workplane()
        .hole(SOCKET_INNER_DIA, depth=SOCKET_HEIGHT)
    )

    # 4. Make Ventilation Hole (Through Base)
    result = (
        result
        .faces("<Z").workplane()
        .hole(HOLE_DIA)
    )

    # 5. Finishing (Chamfer)
    result = (
        result
        .faces(">Z").edges() # 上面の全エッジ（内径円周＋外径円周）
        .chamfer(CHAMFER)
    )

    return result

# --- Execution ---
if __name__ == "__main__":
    # スクリプトの場所を基準に出力パスを決定
    script_dir = os.path.dirname(__file__)

    # 1. Full Model
    print("Generating full model...")
    result_full = generate_stand()
    filename_full = os.path.join(script_dir, "cap_stand_7.step")
    cq.exporters.export(result_full, filename_full)
    print(f"Exported: {filename_full}")

    # 2. Test Piece
    print("Generating test piece...")
    result_test = generate_test_piece()
    filename_test = os.path.join(script_dir, "cap_stand_test.step")
    cq.exporters.export(result_test, filename_test)
    print(f"Exported: {filename_test}")
