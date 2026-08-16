#!/usr/bin/env python3
"""Build an Arabic geomancy chart from four mother figures."""

from __future__ import annotations

import argparse
import json
from typing import Iterable


ELEMENTS = ["火", "风", "水", "土"]
FIGURES = {
    1: ("男人", "1121"),
    2: ("喜悦", "1222"),
    3: ("龙首", "2111"),
    4: ("白色", "2212"),
    5: ("女人", "1211"),
    6: ("龙尾", "1112"),
    7: ("红色", "2122"),
    8: ("悲伤", "2221"),
    9: ("小吉", "1122"),
    10: ("限制", "1221"),
    11: ("结合", "2112"),
    12: ("大吉", "2211"),
    13: ("道路", "1111"),
    14: ("失去", "1212"),
    15: ("群众", "2222"),
    16: ("获得", "2121"),
}
PATTERN_TO_INFO = {pattern: (number, name) for number, (name, pattern) in FIGURES.items()}
NAME_TO_PATTERN = {name: pattern for name, pattern in FIGURES.values()}
NUMBER_TO_PATTERN = {str(number): pattern for number, (_name, pattern) in FIGURES.items()}


def parse_figure(raw: str) -> list[int]:
    stripped = raw.strip()
    if stripped in NAME_TO_PATTERN:
        stripped = NAME_TO_PATTERN[stripped]
    elif stripped in NUMBER_TO_PATTERN:
        stripped = NUMBER_TO_PATTERN[stripped]

    normalized = (
        stripped
        .replace("single", "1")
        .replace("double", "2")
        .replace("..", "2")
        .replace(".", "1")
        .replace("-", "")
        .replace(",", "")
        .replace("/", "")
        .replace(" ", "")
    )
    if len(normalized) != 4 or any(ch not in "12" for ch in normalized):
        raise ValueError(f"Invalid figure {raw!r}; use four values of 1/single or 2/double.")
    return [int(ch) for ch in normalized]


def combine(a: Iterable[int], b: Iterable[int]) -> list[int]:
    # Same parity makes double; mixed parity makes single.
    return [2 if x == y else 1 for x, y in zip(a, b)]


def build_chart(mothers: list[list[int]]) -> list[list[int]]:
    daughters = [[mothers[col][row] for col in range(4)] for row in range(4)]
    figures = mothers + daughters
    figures.append(combine(figures[0], figures[1]))
    figures.append(combine(figures[2], figures[3]))
    figures.append(combine(figures[4], figures[5]))
    figures.append(combine(figures[6], figures[7]))
    figures.append(combine(figures[8], figures[9]))
    figures.append(combine(figures[10], figures[11]))
    figures.append(combine(figures[12], figures[13]))
    figures.append(combine(figures[14], figures[0]))
    return figures


def render_figure(fig: list[int]) -> dict[str, str]:
    return {element: ("单" if value == 1 else "双") for element, value in zip(ELEMENTS, fig)}


def figure_info(fig: list[int]) -> tuple[int | None, str | None, str]:
    pattern = "".join(map(str, fig))
    number, name = PATTERN_TO_INFO.get(pattern, (None, None))
    return number, name, pattern


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a 16-house Arabic geomancy chart.")
    parser.add_argument("mothers", nargs=4, help="Four mother figures as names, numbers, or 火风水土 patterns, e.g. 男人 16 1212 道路")
    parser.add_argument("--details", action="store_true", help="Show number, pattern, and row details in readable text.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of readable text.")
    args = parser.parse_args()

    mothers = [parse_figure(raw) for raw in args.mothers]
    chart = build_chart(mothers)
    data = []
    for i, fig in enumerate(chart):
        number, name, pattern = figure_info(fig)
        data.append({"house": i + 1, "number": number, "name": name, "figure": pattern, "rows": render_figure(fig)})

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    labels = ["母亲"] * 4 + ["女儿"] * 4 + ["侄女"] * 6 + ["评判", "总评/归结"]
    for item, label in zip(data, labels):
        name = item["name"] or "未知卦"
        if args.details:
            rows = " ".join(f"{k}:{v}" for k, v in item["rows"].items())
            identity = f"{item['number']}.{name}" if item["number"] else name
            print(f"{item['house']:>2}宫 {label:<6} {identity:<8} {item['figure']}  {rows}")
        else:
            print(f"{item['house']:>2}宫 {label:<6} {name}")


if __name__ == "__main__":
    main()
