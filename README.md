# Real Uniform Generator

Blender 4.3以降（Blender 5.2を含む）向けの、日本の制服プリーツスカート生成アドオンです。

## v0.2.0の機能

- 明示的な折り面で構成するナイフプリーツ
- ウエスト側ではプリーツを縫い止め、裾に向かって開く形状
- ウエスト、奥行、丈、裾幅、プリーツ数、プリーツ深さの調整
- 生地厚、ウエストベルト、ベルト重なり、裾芯
- 裏地の自動生成と丈調整
- ウエスト・裾・各プリーツの縫製ステッチ
- 脇ファスナーテープ、ファスナー歯、引き手、ホック・アイ
- 解析UVを生成した外布と裏地
- 冬服濃紺、夏服濃紺、チャコール、ブラックの生地プリセット
- 縦横の織り目、微細繊維、色むら、粗さむらを含むプロシージャル材質
- 確認用の床、照明、カメラを自動配置
- PNGプレビューレンダリング
- `.blend` コピー保存
- GLB / FBX / OBJへの非破壊書き出し

## インストール

### GitHub Actionsの配布ZIPを使う方法

1. GitHubの `Actions` を開きます。
2. 最新の `Validate and Package Blender Add-on` を開きます。
3. Artifactsから `real_uniform_generator-v0.2.0` をダウンロードします。
4. Blenderで `Edit > Preferences > Add-ons > Install from Disk` を選択します。
5. ダウンロードしたZIPを指定します。

### リポジトリZIPから作る方法

1. リポジトリを `Code > Download ZIP` でダウンロードして展開します。
2. `real_uniform_generator` フォルダだけをZIP圧縮します。
3. ZIP直下に `__init__.py` と `blender_manifest.toml` があることを確認します。
4. Blenderの `Install from Disk` からインストールします。

## 使用方法

1. 3Dビューで `N` キーを押します。
2. `Uniform` タブを開きます。
3. シルエット、プリーツ、縫製、生地を設定します。
4. `制服スカートを生成` を押します。
5. `確認用スタジオを作成` で質感を確認します。
6. 必要に応じてBLEND、GLB、FBX、OBJで保存します。

## ファイル構成

```text
real_uniform_generator/
├── __init__.py
├── constants.py
├── properties.py
├── geometry.py
├── materials.py
├── exporter.py
├── preview.py
├── operators.py
├── ui.py
└── blender_manifest.toml
```

## 制約

このリポジトリのCIではPython構文、パッケージ構成、Blender Extensionマニフェスト、配布ZIP生成を検証します。Blender本体での形状・レンダリング確認は、Blender 5.2へインストールして行ってください。発生したエラーは、Traceback全文をIssueまたはチャットに貼り付ければ修正できます。
