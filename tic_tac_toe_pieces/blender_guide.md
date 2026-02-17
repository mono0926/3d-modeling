# Blenderでのイチゴ・モデリングガイド

Blenderを使用して、AMSでの2色印刷に対応した「Apple絵文字風」のイチゴを作成します。

## 1. 初期準備

まず、Blenderの単位を3Dプリントに適した `mm` に設定します。

1. 右側のプロパティパネルで **Scene Properties**（円錐と球のアイコン）をクリック。
2. **Units** を開き、以下の通り設定：
   - **Unit System**: `Metric`
   - **Length**: `Millimeters`
   - **Unit Scale**: `0.001` (1mm=1単位にする場合) または `1.0` のまま進めます。

## 2. 自動形状生成 (Pythonスクリプト)

手動での作成は難しいため、まずScripting機能を使って「理想的な雫型のベース」と「ヘタ」を生成します。

1. Blender上部のタブから **Scripting** を選択。
2. **+ New** をクリックして、以下のコードを貼り付けて **Run Script** を押してください。

```python
import bpy
import bmesh
import math

# パラメータ
SIZE = 16.0
BASE_HEIGHT = 2.0
DECO_HEIGHT = 2.0

def create_strawberry_body():
    # 雫型の作成
    bpy.ops.mesh.primitive_uv_sphere_add(radius=SIZE/2, location=(0,0,0))
    obj = bpy.context.active_object
    obj.name = "Strawberry_Red"

    # 縦に伸ばして下を尖らせる
    obj.scale[2] = 1.1
    bpy.ops.object.transform_apply(scale=True)

    # 底面をフラットにする (Z=0)
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    for v in bm.verts:
        if v.co.z < -SIZE/3:
             v.co.z = -SIZE/3
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.location.z = abs(obj.bound_box[0][2]) # 接地させる

def create_leaves():
    # ヘタ(5枚)の作成
    bpy.ops.mesh.primitive_circle_add(vertices=5, radius=SIZE*0.4, location=(0,0,BASE_HEIGHT + 1.0))
    obj = bpy.context.active_object
    obj.name = "Strawberry_Green"

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.edge_face_add()
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0,0,DECO_HEIGHT)})
    bpy.ops.object.mode_set(mode='OBJECT')

create_strawberry_body()
create_leaves()
```

## 3. 手動での微調整 (スカルプト / 編集モード)

スクリプトで生成されたモデルを「Apple絵文字」に近づけます。

### イチゴ本体 (Red)

- **Object Mode** で本体を選択し、**Sculpt Mode** に切り替え。
- **Grab** ブラシ（黄色いアイコン）を使い、下部を少し左右に広げたり、全体をふっくらさせます。

### ヘタ (Green)

- **Edit Mode** (Tabキー) に入り、各頂点を選択して **Sキー** で拡大縮小したり、**Gキー** で動かして葉の形を整えます。
- 葉の先端を少し浮かせたりすると、よりリアルになります。

## 4. 出力

1. 両方のオブジェクトを選択。
2. **File > Export > STL (.stl)** または **3MF (.3mf)** で保存。
3. Bambu Studioで開き、前述のレイヤー構造に従って着色してください。
