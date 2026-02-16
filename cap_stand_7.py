import cadquery as cq
import math

"""
Project: Bottle Cap Stand for Vase Drying
Date: 2026-02-16
Description:
    花瓶を逆さまにして乾燥させる際に、口が密閉されないように隙間を作るためのスタンド。
    ペットボトルのキャップを7個（中心1＋周囲6）配置して土台とする。

Requirements:
    - キャップ配置: ヘキサゴン配置（中心1, 周囲6）
    - キャップ保持: 円柱状のソケットに嵌め込む（深い凹みではなく、薄いベース＋立ち上がり壁）
    - 通気性: ソケット底面には大きな貫通穴を開ける
    - サイズ感: キャップがスムーズに入るクリアランス確保
    - 出力: 3Dプリンター用STEPファイル

History:
    - Initial Plan: Base plate with recesses.
    - Rev 1: Thin base plate with cylindrical sockets rising up, for material saving and print speed.
    - Rev 2: Added large through-holes in sockets for better ventilation and material reduction.
    - Rev 3: Reduced socket height to 3.0mm based on user feedback (minimal height).
    - Rev 4: Replaced hull() with polygon() as hull() was causing AttributeError in this environment.
"""

# --- Parameters ---
CAP_DIAMETER = 31.0       # キャップ外径 (標準的なサイズ + 余裕)
CLEARANCE = 0.6           # キャップとの隙間 (片側0.3mm)
SOCKET_WALL = 2.0         # ソケットの壁厚
SOCKET_HEIGHT = 3.0       # ソケットの高さ (ベース面からの立ち上がり。ずれ防止の最低限の高さ)
BASE_THICKNESS = 2.0      # ベースプレートの厚み
PITCH = 45.0             # キャップ中心間の距離 (干渉防止)
HOLE_DIA = 15.0           # 底面の通気用貫通穴径
CHAMFER = 0.8             # エッジの面取りサイズ (2.0mm壁に対して1.0mmだと干渉するため0.8mmに縮小)

# --- Derived Design Constants ---
# ソケット外径 = キャップ径 + クリアランス + 壁厚*2
SOCKET_OUTER_DIA = CAP_DIAMETER + CLEARANCE + (SOCKET_WALL * 2)
# ソケット内径 = キャップ径 + クリアランス
SOCKET_INNER_DIA = CAP_DIAMETER + CLEARANCE

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
    BASE_RADIUS = PITCH + (SOCKET_OUTER_DIA / 2.0)

    base = (
        cq.Workplane("XY")
        .polygon(6, BASE_RADIUS * 2) # 対角距離（直径）を指定
        .extrude(BASE_THICKNESS)
        .edges("|Z").fillet(10.0) # 角を丸めて優しくする
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

# --- Execution ---
if __name__ == "__main__":
    result = generate_stand()

    # Export
    filename = "cap_stand_7.step"
    cq.exporters.export(result, filename)
    print(f"Exported: {filename}")
