# Adobe CC / Envato 生地ワークフロー

## 推奨順位

1. 実物スカート、または同じ生地の端切れを撮影
2. Adobe Substance 3D SamplerでPBR化
3. 適切なEnvato素材を補助・比較用に使用
4. アドオンの内蔵PBRは仮素材として使用

## Adobe Substance 3D Sampler

### 写真から作る

1. Substance 3D Samplerで新規プロジェクト・新規マテリアルを作成します。
2. 生地の正面写真をドラッグします。
3. `Image to Material` / `画像からマテリアル` を選びます。
4. 照明・影の除去、Perspective、Crop、Make it Tileを調整します。
5. MetadataのPhysical Sizeを、写真に写した定規に合わせます。
6. HeightとNormalを強くしすぎず、糸の細かな起伏だけが見える状態にします。
7. Roughnessは制服用ウール／ポリエステル混らしく高めに保ちます。
8. PNGで次を出力します。

```text
NavyUniform_BaseColor.png
NavyUniform_Roughness.png
NavyUniform_NormalGL.png
NavyUniform_Height.png
NavyUniform_AO.png  # 任意
```

### Normal形式

Blender向けには `NormalGL` を推奨します。`NormalDX` しかない場合も、アドオンがファイル名を判定して緑チャンネルを反転します。

### Photoshopで補正する場合

- Camera Rawでレンズ補正、ホワイトバランス、遠近を整える
- High Passだけで凹凸を作らない
- 大きな明暗はBase Colorから除去する
- シームレス化はOffsetと修復ブラシを使い、糸の周期を壊さない
- カラーチェッカーやグレーカードがある場合は色基準を合わせる

## Envatoで探す条件

検索語の例:

```text
navy woven suiting fabric seamless texture
navy gabardine fabric PBR
poly viscose uniform fabric texture
dark blue twill wool fabric seamless
woven textile material PBR 4k
```

選定条件:

- 平織り、綾織り、ギャバジン、スーツ地
- シームレスまたは大きな正射影写真
- Base Color / Roughness / Normal / Heightがある
- 糸目が巨大でない
- ニット、デニム、ベルベット、サテン、シルク、レザーは除外
- 強い撮影影、折りじわ、背景グラデーションが焼き付いていない

## Envatoライセンス上の運用

- ダウンロード時にこのプロジェクト用としてライセンス登録します。
- 元画像・PBRマップをGitHub、アドオンZIP、素材集として再配布しません。
- 公開するアドオンには、画像ではなくローカルフォルダ読込機能だけを含めます。
- 第三者へ渡すBLEND/GLBへ素材を埋め込む場合、元素材が抽出可能にならないか契約条件を確認します。
- 配布可能な3Dアセットを作る場合は、実物を自分で撮影した素材、CC0、または再配布を明示的に許可する別ライセンスを優先します。

## アドオンへ読み込む

1. 画像一式を同じフォルダへ置きます。
2. Blenderの `制服` タブを開きます。
3. `生地ソース` を `外部PBRフォルダ` にします。
4. PBRフォルダを指定します。
5. `PBRフォルダを検査` を押します。
6. `テクスチャ実寸` をSamplerのPhysical Sizeと同じ値へ合わせます。
7. `制服スカートを生成` を押します。
