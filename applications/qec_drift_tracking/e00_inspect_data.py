"""
E00.1 — inspect the Willow 105Q Zenodo archive format.

Read the top-level README + sample a small d=5 experiment to understand:
- file structure inside the zip (directories, naming convention per distance / basis / round count)
- detector-event format (Stim circuit? numpy array? HDF5?)
- timestamp granularity — per-run vs per-shot (Phase 0 flagged this as a gotcha)
- observable flip ground-truth availability
"""

from __future__ import annotations
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
ZIP_PATH = HERE / "data" / "raw" / "google_105Q_surface_code_d3_d5_d7.zip"


def main():
    if not ZIP_PATH.exists():
        print(f"[E00.1] zip not downloaded yet: {ZIP_PATH}")
        return

    print(f"[E00.1] inspecting {ZIP_PATH} ({ZIP_PATH.stat().st_size / 1e9:.2f} GB)", flush=True)

    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        names = z.namelist()
        print(f"[E00.1] {len(names)} files in archive", flush=True)
        # Top 30 entries
        for n in names[:30]:
            info = z.getinfo(n)
            print(f"  {n}  ({info.file_size/1e6:.1f} MB)", flush=True)
        if len(names) > 30:
            print(f"  ... {len(names) - 30} more", flush=True)

        # Find README if present
        readme_candidates = [n for n in names if "README" in n.upper() or "readme" in n.lower()]
        for readme in readme_candidates[:3]:
            print(f"\n[E00.1] === {readme} ===", flush=True)
            with z.open(readme) as f:
                content = f.read().decode("utf-8", errors="replace")
                print(content[:4000], flush=True)

        # Find a d=5 sample file — detect naming convention
        d5_files = [n for n in names if "d5" in n.lower() or "distance5" in n.lower() or "distance=5" in n.lower()]
        print(f"\n[E00.1] {len(d5_files)} d=5 files detected", flush=True)
        for f in d5_files[:5]:
            print(f"  {f}", flush=True)

        # If any .stim files, print one
        stim_files = [n for n in names if n.endswith(".stim")]
        if stim_files:
            print(f"\n[E00.1] === sample {stim_files[0]} ===", flush=True)
            with z.open(stim_files[0]) as f:
                content = f.read().decode("utf-8", errors="replace")
                print(content[:2000], flush=True)

        # Directory structure summary
        print("\n[E00.1] top-level directories:", flush=True)
        dirs = set()
        for n in names:
            parts = n.split("/")
            if len(parts) > 1:
                dirs.add(parts[0])
        for d in sorted(dirs):
            print(f"  {d}/", flush=True)


if __name__ == "__main__":
    main()
