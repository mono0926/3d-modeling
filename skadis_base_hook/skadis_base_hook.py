import os
import cadquery as cq
from ocp_vscode import show_object

"""
設計要件:
    - IKEA Skadisペグボード用の汎用フックベースのモデリング。
    - 最善の返し（ドロップ）の長さを5.0mmに設定し、保持力と着脱のしやすさを両立。
    - P2SなどのFDMプリンターで強度を最大化するため、側面（XY平面）を下にしてプリントする設計。
    - 応力集中を防ぐため、首と返しの交点にR1.5のフィレットを配置。スコーディスの穴底面（半円弧）に長方形の底面が乗ることで生じる自然な浮き(約1.8mm)により、基板との干渉なく強固なフィレットを形成。

推奨フィラメント:
    - PLA, PETG, ABS等。層間強度が求められるため、粘りのあるPETGなどを推奨。

推奨スライサー設定:
    - Wall Loops (壁の数): 4〜6（強度を出すため、薄い部分はほぼ壁で埋めるのが理想）
    - Infill Density: 25% 以上

印刷統計（予想）:
    - 印刷時間 約10分以内、フィラメント数グラム

履歴とプロンプト経緯:
    - 詳細は同ディレクトリの history.md を参照。
"""

# ==========================================
# 共通パラメーター
# ==========================================
BOARD_THICKNESS = 5.0
NECK_LENGTH = 5.4      # ボード厚(5.0) + フィレット・干渉避けの余裕(0.4)
NECK_HEIGHT = 5.0      # スコーディスの穴(15mm高)に対し十分なスライド余裕を持つ高さ
HOOK_DROP = 5.0        # 返し（ボード裏に引っ掛かる部分）の長さ。ベストな長さは4.0〜5.0mm。
HOOK_THICKNESS = 2.5   # 返し部分の厚み
HOOK_WIDTH = 4.8       # プリント時のZ方向の厚み。穴幅5.0mmに対して0.2mmのクリアランス

def create_skadis_hook_profile() -> cq.Wire:
    """
    フック部分の2Dプロファイル（XY平面上のWire）を作成します。
    原点(0,0)は、ネックの下側手前（フロントパネル側）になります。
    """
    p_top_front = (0, NECK_HEIGHT)
    p_top_back = (NECK_LENGTH + HOOK_THICKNESS, NECK_HEIGHT)
    p_bottom_back = (NECK_LENGTH + HOOK_THICKNESS, -HOOK_DROP)
    p_bottom_inner = (NECK_LENGTH, -HOOK_DROP)
    p_inner_corner = (NECK_LENGTH, 0)
    p_bottom_front = (0, 0)

    wire = (
        cq.Workplane("XY")
        .polyline([
            p_top_front,
            p_top_back,
            p_bottom_back,
            p_bottom_inner,
            p_inner_corner,
            p_bottom_front
        ]).close()
    )
    return wire.val()

def get_base_hook() -> cq.Workplane:
    """
    他の形状と結合（fuse）して使い回せるフックの基本ソリッドを生成します。
    側面を下にしてプリントできるよう、Z方向に4.8mm押し出します。
    """
    profile = create_skadis_hook_profile()
    hook = cq.Workplane("XY").add(profile).toPending().extrude(HOOK_WIDTH)

    # 1. 内側のコーナーに応力を逃がす広めのフィレット（R1.5）
    # NearestToPointSelector を使って確実に対象のエッジを選択
    hook = hook.edges(cq.selectors.NearestToPointSelector((NECK_LENGTH, 0, HOOK_WIDTH/2))).fillet(1.5)

    # 2. 差し込みやすくするための先端の丸み（R1.0程度、裏側はR0.5）
    hook = hook.edges(cq.selectors.NearestToPointSelector((NECK_LENGTH + HOOK_THICKNESS, -HOOK_DROP, HOOK_WIDTH/2))).fillet(1.0)
    hook = hook.edges(cq.selectors.NearestToPointSelector((NECK_LENGTH, -HOOK_DROP, HOOK_WIDTH/2))).fillet(0.5)

    # 3. ボード裏の上面に当たる角の面取り（スムーズな挿入のため）
    hook = hook.edges(cq.selectors.NearestToPointSelector((NECK_LENGTH + HOOK_THICKNESS, NECK_HEIGHT, HOOK_WIDTH/2))).chamfer(1.0)

    return hook

def create_sample_utility_hook():
    """
    実用的なサンプルとして、輪ゴムや鍵などを引っ掛けられるJ字型フックを作成します。
    フロントのベースプレート機能も組み合わせた汎用的な形状です。
    """
    app_hook_length = 15.0  # 前方に突き出すフックの長さ
    app_hook_height = 8.0   # フックの立ち上がり

    hook_base = get_base_hook()

    # ベースプレートの厚み
    base_thickness = 3.0

    j_hook_profile = (
        cq.Workplane("XY")
        .polyline([
            (0, NECK_HEIGHT),                                # 1. ベースプレート右上（フック基部と接続）
            (0, -12.0),                                      # 2. ベースプレート右下
            (-app_hook_length, -12.0),                       # 3. J字フックの左下
            (-app_hook_length, -12.0 + app_hook_height),     # 4. J字フックの左上（先端）
            (-app_hook_length + 3.0, -12.0 + app_hook_height), # 5. J字フック先端の内側
            (-app_hook_length + 3.0, -12.0 + 3.0),           # 6. J字フックの谷底
            (-base_thickness, -12.0 + 3.0),                  # 7. トレイ部からベースプレートへの立ち上がり
            (-base_thickness, NECK_HEIGHT)                   # 8. ベースプレート左上
        ]).close()
    )

    j_hook = cq.Workplane("XY").add(j_hook_profile).toPending().extrude(HOOK_WIDTH)

    # 指先などが触れるフック外側の角を滑らかにする
    j_hook = j_hook.edges("|Z").fillet(1.0)

    # 基本のSkadisフックと結合
    result = hook_base.union(j_hook)

    return result

if __name__ == "__main__":
    # サンプルの生成
    final_model = create_sample_utility_hook()

    # プレビュー表示
    show_object(final_model, name="Skadis_Sample_Hook")

    # STEPエクスポート
    output_path = os.path.join(os.path.dirname(__file__), "skadis_base_hook.step")
    cq.exporters.export(final_model, output_path)
    print(f"Exported STEP file to {output_path}")
