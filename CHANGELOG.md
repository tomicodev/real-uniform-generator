# Changelog

## 0.5.0 — 2026-07-25

### Rebuilt

- 放射状の波形スカートを廃止し、連続したナイフプリーツ型紙エンジンへ移行
- ウエスト・ヒップ周長から楕円断面を算出
- 縫い止まり、解放区間、自由部分を分離
- 外部裾リングを廃止し、内側裾見返しへ変更
- ウエストベルトを中空・開き付き構造へ変更

### Added

- 実寸入力
- 左脇／右脇／後ろ中心の開き位置
- 縫い代、左右テープ、ナイロンコイル、小型スライダー、上下止め、ホック
- 内側構造の表示切替
- まつり縫い／ミシン縫い
- 物理スケールUV
- Adobe Substance / Envato等の外部PBRフォルダ読込
- BaseColor、Roughness、NormalGL、NormalDX、Height、AOの自動判定
- DirectX NormalのY反転
- 4096px内蔵PBR
- Adobe/Envato素材制作ガイド
- 型紙数理テスト

### Material changes

- 内蔵生地の色むらと凹凸を大幅に弱め、樹脂的な見え方を抑制
- Roughnessを高め、Sheenを抑制
- HeightをNormalとは別チャンネルで生成

### Known limitations

- 自動Cloth緩和はまだ既定生成へ組み込んでいません
- 実物生地を用いない内蔵PBRは、近接Heroショット用の最終素材ではありません
- 人物へのフィッティングは対象ボディごとの調整が必要です
