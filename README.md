# Real Uniform Generator

Blender 4.3以降（Blender 5.2 LTSを含む）向けの、日本の制服プリーツスカート生成アドオンです。

## v0.5.0 — Pattern & Material Foundation

前版の「楕円筒へ周期的な凹凸を付ける方式」を廃止し、縫製される一枚布の経路を追う型紙ベースのエンジンへ置き換えました。

- 完成ウエスト周長・完成ヒップ周長・丈・ヒップラインを実寸入力
- 表プリーツ、折り山、奥プリーツ、折り返しを連続した一枚布として生成
- ウエスト側の縫い止まり、解放区間、自由落下区間を分離
- 外側へ露出する裾リングを廃止し、各プリーツに追従する内側見返しを生成
- 左脇／右脇／後ろ中心の実際の開き線とコンシールファスナー構造
- 左右の縫い代、ファスナーテープ、細いナイロンコイル、小型スライダー、ホック
- 通常表示では内部構造を隠し、確認時だけ表示可能
- まつり縫い／外側ミシン縫いの選択
- 物理スケールUV
- 内蔵PBR、またはAdobe Substance 3D Sampler・Envato等から書き出した外部PBRセットの自動読込
- Base Color / Roughness / NormalGL / NormalDX / Height / AOの自動判定
- GLB / FBX / OBJの非破壊書き出し、BLENDコピー保存
- 円形ステージを使わないニュートラルな確認用スタジオ

## インストール

GitHub Actionsの最新Artifact、またはローカルで作成した `real_uniform_generator-v0.5.0.zip` を、BlenderのPreferencesから `Install from Disk` で選択します。

インストール後、3Dビューで `N` キーを押し、右側の **「制服」** タブを開きます。

## 最初の推奨設定

```text
ウエスト仕上がり  68 cm
ヒップ仕上がり    92 cm
スカート丈          48 cm
ヒップライン        18 cm
プリーツ数          20
奥プリーツ深さ      2.8 cm
縫い止まり          10.5 cm
解放区間            5.5 cm
表地厚              1.25 mm
裾折り返し          4 cm
裾の縫い方          まつり縫い
ファスナー          左脇・18 cm
```

## Adobe CC / Envatoを使う場合

最も高い品質は、実物の生地見本を撮影し、Adobe Substance 3D Samplerの「画像からマテリアル」でPBR化する方法です。Envatoの素材もローカルの参考・レンダリング用として読み込めます。

詳しい手順は以下をご覧ください。

- [`docs/ADOBE_ENVATO_WORKFLOW.md`](docs/ADOBE_ENVATO_WORKFLOW.md)
- [`docs/FABRIC_CAPTURE_GUIDE.md`](docs/FABRIC_CAPTURE_GUIDE.md)
- [`docs/REALISM_SPEC.md`](docs/REALISM_SPEC.md)

> **Envato素材について**  
> Envatoの元画像やPBRマップを、この公開リポジトリや配布アドオンへ同梱しないでください。プロジェクト単位でライセンス登録し、契約条件に従ってローカル利用してください。第三者へ抽出可能な素材として再配布する用途には使いません。

## Windowsで一括ビルド・検査

リポジトリ直下の `BUILD_AND_TEST.bat` をダブルクリックするか、PowerShellで次を実行します。

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build_and_test.ps1
```

既定のBlenderパス:

```text
C:\Program Files\Blender Foundation\Blender 5.2\blender.exe
```

成功すると以下が表示されます。

```text
RUG_PATTERN_TEST_OK
RUG_SMOKE_TEST_OK
RUG_INSTALLED_EXTENSION_TEST_OK
```

配布ZIP:

```text
dist\real_uniform_generator-v0.5.0.zip
```

## 現段階の位置づけ

v0.5.0は、フォトリアル化のための**構造とマテリアル入出力の基盤**です。実物と見分けにくい最終品質には、次の入力が必要です。

1. 再現対象となる一着の実寸
2. 実物生地の接写、または適切にライセンスされたPBR素材
3. 正面・側面・背面・内側の比較写真
4. 必要に応じたCloth緩和と人物へのフィッティング

数式だけで「制服風」にするのではなく、特定の一着をデジタルツインとして合わせ込む方針です。
