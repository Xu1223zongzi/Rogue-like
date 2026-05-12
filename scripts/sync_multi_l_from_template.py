from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.world.assembled_world import _load_component_library


MAPS = ("第二张地图", "初始地图")
FAMILIES = ("多L_", "多L反_", "多L反2_")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync all multi-L resource files from the current 多L_01 structure while preserving socket geometry.",
    )
    parser.add_argument(
        "--template-map",
        default="第二张地图",
        choices=MAPS,
        help="Map folder whose 多L_01.txt is treated as the structural template.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print files that would be updated without writing them.",
    )
    return parser.parse_args()


def leading_walls(row: str) -> int:
    count = 0
    while count < len(row) and row[count] == "#":
        count += 1
    return count


def load_template_tokens(root: Path, template_map: str) -> dict[str, str]:
    template_path = root / "maps" / template_map / "特殊连接通道" / "多L_01.txt"
    rows = template_path.read_text(encoding="utf-8").splitlines()
    if len(rows) != 10:
        raise ValueError(f"Expected 10 rows in template, got {len(rows)}: {template_path}")

    top_start = leading_walls(rows[0])
    bottom_start = leading_walls(rows[9])
    if top_start == bottom_start:
        raise ValueError("Template 多L_01 must have different top/bottom starts to infer the current structure.")

    return {
        "top_cap": rows[0][top_start : top_start + 4],
        "top_half": rows[2][top_start : top_start + 4],
        "bottom_cap": rows[7][bottom_start : bottom_start + 4],
        "bottom_half": rows[9][bottom_start : bottom_start + 4],
    }


def build_rows(top_start: int, bottom_start: int, right_x: int, tokens: dict[str, str]) -> list[str]:
    width = right_x + 1
    min_start = min(top_start, bottom_start)

    rows = [
        "#" * top_start + tokens["top_cap"] + "#" * (width - top_start - 4),
        "#" * top_start + tokens["top_cap"] + "#" * (width - top_start - 4),
        "#" * top_start + tokens["top_half"] + "#" * (width - top_start - 4),
        "#" * min_start + "." * (width - min_start),
        "#" * min_start + "." * (width - min_start),
        "#" * min_start + "." * (width - min_start),
        "#" * min_start + "." * (width - min_start),
        "#" * bottom_start + tokens["bottom_cap"] + "#" * (width - bottom_start - 4),
        "#" * bottom_start + tokens["bottom_cap"] + "#" * (width - bottom_start - 4),
        "#" * bottom_start + tokens["bottom_half"] + "#" * (width - bottom_start - 4),
    ]
    return rows


def detect_newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def sync_map(root: Path, map_name: str, tokens: dict[str, str], dry_run: bool) -> int:
    library = _load_component_library(map_name)
    changed = 0
    folder = root / "maps" / map_name / "特殊连接通道"
    for path in sorted(folder.glob("多L*.txt")):
        if not path.stem.startswith(FAMILIES):
            continue
        component = library.get(f"特殊连接通道/{path.stem}")
        if component is None:
            continue
        top = component.sockets.get("top")
        bottom = component.sockets.get("bottom")
        right = component.sockets.get("right")
        if top is None or bottom is None or right is None:
            continue
        rows = build_rows(top[0] - 2, bottom[0] - 2, right[0], tokens)
        old_text = path.read_text(encoding="utf-8")
        newline = detect_newline(old_text)
        new_text = newline.join(rows) + newline
        if normalize_text(old_text) == normalize_text(new_text):
            continue
        changed += 1
        if dry_run:
            print(f"would update {map_name}/{path.name}")
            continue
        path.write_text(new_text, encoding="utf-8")
        print(f"updated {map_name}/{path.name}")
    return changed


def main() -> None:
    args = parse_args()
    root = ROOT
    template_root = root / "maps" / args.template_map / "特殊连接通道"
    if not template_root.exists():
        raise FileNotFoundError(f"Template map folder not found: {template_root}")

    tokens = load_template_tokens(root, args.template_map)
    total = 0
    for map_name in MAPS:
        total += sync_map(root, map_name, tokens, args.dry_run)
    mode = "would update" if args.dry_run else "updated"
    print(f"{mode} {total} files")


if __name__ == "__main__":
    main()