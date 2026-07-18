# posehud-decoder

`PositionHUD.shader`が画面に焼き込むビットグリッドを、スクリーンキャプチャ経由で座標・姿勢に戻すPythonライブラリ

## セットアップ

```bash
uv sync
```

## 使い方

```python
from posehud import poses

for pose in poses():
    print(pose.position)
```

実行例は `examples/demo.py` を参照。

## 注意

シェーダー側の `_BlockPx` / `_OffsetX` / `_OffsetY` を変更した場合は、`src/posehud/spec.py` の同名定数も必ず合わせること。1pxでもズレるとマジックナンバー不一致で読めなくなる。
