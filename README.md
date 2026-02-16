## AI活用の3Dモデリング

- [CadQuery](https://github.com/CadQuery/cadquery)を利用前提

### 環境構築

特にApple Silicon Macでpipを使ったCadQueryインストールは失敗しがちなので、condaを使うことを推奨。

Miniforgeインストール

```sh
brew install miniforge
```

初期設定

```sh
conda init zsh
source ~/.zshrc # 再起動でもOK
```

Python 3.11で専用環境を作成

```sh
conda create -n cq-conda-env python=3.11 -c conda-forge
```

CadQueryをインストール

```sh
# 環境に入る
conda activate cq-conda-env
# conda-forge経由でCadQueryをインストール
conda install -c conda-forge cadquery
```

### 使い方

環境に入る(プレーンな環境では毎回初めに実行必要)。
(`.envrc`が設定済みなので、direnv導入済みなら自動実行される。)

```sh
conda activate cq-conda-env
```

以下など任意のスクリプトを実行すると、stepファイルが出力される。

```
python cap.py
```

VS Code系エディタの場合、Python: Select Interpreterから、`Python 3.11.x ('cq-conda-env': conda)`を選択して実行ボタン押すだけで良い。

### stapファイルの扱い

stepファイルは、Bambu Studioなどでそのまま開けるが、Autodesk Fusionを経由したい場合は以下。

1. Autodesk Fusionで開く
2. 3Dプリントのエクスポートで3MFファイルとして出力
3. Bambu Studioで開く
