# Real Uniform Generator

Blender 5.2向けの、日本の冬制服用プリーツスカート生成アドオンです。

## v0.6.0 — Normal Modules & Verified Generator

Base64 runtime payloadを廃止し、通常の複数Pythonモジュール構成へ移行しました。3Dビューの **制服** タブで `制服スカートを生成` を押すと、既定の実寸・縫製仕様からスカートを再生成できます。

### 生成構造

- 完成ウエスト68cm、完成ヒップ92cm、丈48cm、ヒップライン18cm
- 20本ナイフプリーツ、奥プリーツ2.8cm
- ウエストから10.5cmを縫い止め、その下5.5cmで段階的に解放
- 表面、折山、奥プリーツ、次の表面を一枚の連続布として生成
- 裾4cmは外布そのものを内側へ折り返し、独立した裾リングを作らない
- 表地厚1.25mm
- 表ベルト、上端折り、内側見返し、接着芯を持つ3.5cm幅ウエストベルト
- 左脇コンシールファスナー、内側の縫い代・テープ・コイル・小型スライダー
- 裏地付き
- 実寸スケールUV

### マテリアル

- 内蔵の濃紺ウール調マテリアル
- 外部PBRフォルダの自動認識
- Base Color / Roughness / Normal OpenGL / Normal DirectX / Height / AO
- DirectX NormalのY反転
- Metallic 0、Coat 0、弱いSheen
- Normal・Height・AO強度を調整可能
- テクスチャ実幅と織り目サイズをcm単位で設定可能
- Eevee / Cycles対応

### 出力

- GLB / FBX / OBJ
- 元ファイルを上書きしないBLENDコピー保存
- 正面確認用レンダー
- 内部検証用の正面・側面・背面・内側・ファスナービューは `preview.py` から生成可能

## インストール

GitHub Actionsの最新Artifact、またはローカルで作成した `real_uniform_generator-v0.6.0.zip` を、BlenderのPreferencesから `Install from Disk` で選択します。

インストール後、3Dビューで `N` キーを押し、右側の **制服** タブを開きます。

## 既定仕様

```text
ウエスト仕上がり    68 cm
ヒップ仕上がり      92 cm
スカート丈          48 cm
ヒップライン        18 cm
ナイフプリーツ数    20
奥プリーツ深さ      2.8 cm
縫い止め長さ        10.5 cm
プリーツ解放長さ    5.5 cm
表地厚              1.25 mm
裾折り返し          4 cm
ベルト幅            3.5 cm
ファスナー          左脇・18 cm
裏地丈              37 cm
```

## 外部PBRのファイル名例

```text
uniform_wool_basecolor.png
uniform_wool_roughness.png
uniform_wool_normal_opengl.png
uniform_wool_normal_directx.png
uniform_wool_height.png
uniform_wool_ao.png
```

外部素材のライセンス条件に従い、抽出可能な元画像を公開リポジトリや配布ZIPへ同梱しないでください。

## Windowsで一括ビルド・検査

リポジトリ直下の `BUILD_AND_TEST.bat` を実行するか、PowerShellで次を実行します。

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_and_test.ps1
```

既定のBlenderパス:

```text
C:\Program Files\Blender Foundation\Blender 5.2\blender.exe
```

合格時の表示:

```text
RUG_PATTERN_TEST_OK
RUG_SMOKE_TEST_OK
RUG_INSTALLED_EXTENSION_TEST_OK
```

配布ZIP:

```text
dist\real_uniform_generator-v0.6.0.zip
```

## 品質調整

v0.6.0は、標準仕様を安定して再生成する構造実装です。特定の制服をデジタルツインとして合わせ込む場合は、実物の採寸、正面・側面・背面・内側写真、実物生地のPBR、対象ボディへのフィッティングを追加してください。
