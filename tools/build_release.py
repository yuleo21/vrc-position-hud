import argparse
import io
import re
import shutil
import tarfile
import zipfile
from pathlib import Path

GUID_RE = re.compile(rb"^guid:\s*([0-9a-fA-F]{32})\s*$", re.MULTILINE)
DECODER_EXCLUDE = shutil.ignore_patterns(
    ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "dist", "build", "*.pyc"
)


def read_guid(meta_path: Path) -> str:
    m = GUID_RE.search(meta_path.read_bytes())
    if not m:
        raise SystemExit(f"guid not found in {meta_path}")
    return m.group(1).decode("ascii")


def add_bytes(tar: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mtime = 0
    info.mode = 0o644
    tar.addfile(info, io.BytesIO(data))


def build_unitypackage(root: Path, assets_dir: Path, out_path: Path) -> None:
    metas = sorted(p for p in assets_dir.rglob("*.meta"))
    if not metas:
        raise SystemExit(f"no .meta files under {assets_dir}")

    seen: dict[str, Path] = {}
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(out_path, "w:gz") as tar:
        for meta in metas:
            asset = meta.with_suffix("")  # foo.prefab.meta -> foo.prefab
            if not asset.exists():
                raise SystemExit(f"orphan meta (asset missing): {meta}")

            guid = read_guid(meta)
            if guid in seen:
                raise SystemExit(f"duplicate guid {guid}: {seen[guid]} / {asset}")
            seen[guid] = asset

            pathname = asset.relative_to(root).as_posix()
            add_bytes(tar, f"{guid}/pathname", pathname.encode("utf-8"))
            add_bytes(tar, f"{guid}/asset.meta", meta.read_bytes())
            if asset.is_file():
                add_bytes(tar, f"{guid}/asset", asset.read_bytes())

    print(f"created: {out_path} ({len(seen)} assets)")


def build_booth_zip(root: Path, unity_package: Path, out_path: Path) -> None:
    release_name = out_path.stem
    staging = out_path.parent / "_staging" / release_name
    if staging.parent.exists():
        shutil.rmtree(staging.parent)
    staging.mkdir(parents=True)

    try:
        for name in ("LICENSE", "README.md"):
            shutil.copy2(root / name, staging / name)
        shutil.copy2(unity_package, staging / unity_package.name)
        shutil.copytree(root / "decoder", staging / "decoder", ignore=DECODER_EXCLUDE)

        out_path.unlink(missing_ok=True)
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(staging.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(staging.parent).as_posix())
    finally:
        shutil.rmtree(staging.parent, ignore_errors=True)

    print(f"created: {out_path}")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True, help="例: 1.0.0")
    ap.add_argument("--assets", default=str(root / "Assets"))
    ap.add_argument("--out-dir", default=str(root / "dist"))
    args = ap.parse_args()

    version = args.version.lstrip("v")
    if not re.fullmatch(r"\d+(\.\d+)*", version):
        raise SystemExit(f"unexpected version: {args.version}")

    out_dir = Path(args.out_dir).resolve()
    unity_package = out_dir / f"PositionHUD_v{version}.unitypackage"

    build_unitypackage(root, Path(args.assets).resolve(), unity_package)
    build_booth_zip(root, unity_package, out_dir / f"PositionHUD_v{version}.zip")


if __name__ == "__main__":
    main()
