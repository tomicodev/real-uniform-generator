# Real Uniform Generator

Blender 4.3以降（Blender 5.2を含む）向けの、日本の制服プリーツスカート生成アドオンです。

## v0.2.0の機能

- 明示的な折り面で構成するナイフプリーツ
- ウエスト側ではプリーツを縫い止め、裾に向かって開く形状
- 折り線をシャープエッジとして保持し、面の途中だけを滑らかにする法線処理
- ウエスト、奥行、丈、裾幅、プリーツ数、プリーツ深さの調整
- 生地厚、ウエストベルト、ベルト重なり、裾芯
- 裏地の自動生成と丈調整
- ウエスト・裾・各プリーツ・脇接ぎの縫製ステッチ
- 脇ファスナーテープ、ファスナー歯、引き手、ホック・アイ
- 外布と裏地のUV
- 冬服濃紺、夏服濃紺、チャコール、ブラックの生地プリセット
- Base Color、Roughness、NormalのPBR画像をBlender内で生成してパック
- 512 / 1024 / 2048 pxのPBRテクスチャ解像度
- 縦糸・横糸・綾織り・微細繊維・色むら・粗さむらを含む生地表現
- 確認用の床、照明、カメラを自動配置
- PNGプレビューレンダリング
- `.blend` コピー保存
- GLB / FBX / OBJへの非破壊書き出し
- GLBへの画像内包、FBXへのテクスチャ埋め込み、OBJ用PNG出力

## インストール

### GitHub Actionsの公式ビルドZIPを使う方法

1. GitHubの `Actions` を開きます。
2. 最新の `Validate Package and Test Blender Add-on` を開きます。
3. Artifactsから `real_uniform_generator-v0.2.0` をダウンロードします。
4. BlenderのPreferencesから `Install from Disk` を選択します。
5. ダウンロードしたZIPを指定します。

同じ実行の `blender-runtime-outputs` には、Blender 5.2で実際に生成したプレビューPNG、BLEND、GLB、FBX、OBJ、MTL、PBR画像が入ります。`real_uniform_generator-v0.2.0-fallback` は静的検証のみで作成する予備ZIPです。

### リポジトリZIPから手動で作る方法

1. リポジトリを `Code > Download ZIP` でダウンロードして展開します。
2. `real_uniform_generator` フォルダを開き、その**中身**をZIP圧縮します。
3. ZIP直下に `__init__.py`、`blender_manifest.toml`、`LICENSE.txt` があることを確認します。
4. Blenderの `Install from Disk` からインストールします。

## 使用方法

1. 3Dビューで `N` キーを押します。
2. `Uniform` タブを開きます。
3. シルエット、プリーツ、縫製、生地、PBR解像度を設定します。
4. `制服スカートを生成` を押します。
5. `確認用スタジオを作成` で質感を確認します。
6. 必要に応じてBLEND、GLB、FBX、OBJで保存します。

## Windowsで一括確認する

`BUILD_AND_TEST.bat` をダブルクリックするか、リポジトリ直下で次を実行します。

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_and_test.ps1
```

既定では以下のBlenderを使用します。

```text
C:\Program Files\Blender Foundation\Blender 5.2\blender.exe
```

この処理は以下を順に実行します。

1. Blender公式のExtension Buildコマンドで配布ZIPを作成
2. Blender公式のExtension ValidateコマンドでZIPを検証
3. ソースツリーを直接読み込む生成・書き出しテスト
4. 隔離したBlenderユーザー環境へZIPを実際にインストールして有効化
5. インストール済みアドオンから生成、プレビュー、全形式書き出しを実行

検査対象は以下です。

- スカート、ウエストベルト、裏地、縫製、ファスナー、ホックの生成
- 頂点数、UV、マテリアル、プリーツのシャープエッジ
- Base Color、Roughness、Normal画像の生成とパック
- プレビューPNG
- GLB、FBX、OBJ、MTL、外部PNG、BLEND

成功時はコンソールに次の2行が表示されます。

```text
RUG_SMOKE_TEST_OK
RUG_INSTALLED_EXTENSION_TEST_OK
```

配布ZIPは次に作成されます。

```text
dist\real_uniform_generator-v0.2.0.zip
```

## ファイル構成

```text
real_uniform_generator/
├── __init__.py
├── constants.py
├── properties.py
├── geometry.py
├── finishing.py
├── materials.py
├── textures.py
├── exporter.py
├── preview.py
├── operators.py
├── ui.py
├── LICENSE.txt
└── blender_manifest.toml

tests/
├── blender_smoke_test.py
└── installed_extension_smoke_test.py

tools/
└── build_and_test.ps1

BUILD_AND_TEST.bat
```

## 検証範囲

GitHub ActionsはPython構文、パッケージ構成、Blender Extensionマニフェスト、ZIP構造を検査した後、公式Linux版Blender 5.2 Stableを起動します。Blender公式CLIでZIPをビルド・検証し、隔離環境へ実際にインストールして、形状・PBR材質・プレビュー・BLEND・GLB・FBX・OBJの生成まで検査します。Windowsでは `BUILD_AND_TEST.bat` から同等の検証を実行できます。
