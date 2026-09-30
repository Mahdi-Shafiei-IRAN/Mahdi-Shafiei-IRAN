"""Snake Trail: a snake that eats its way through the contribution heatmap (pure SMIL, no JS)."""

from __future__ import annotations

from ..context import BuildContext
from ..svg import Cell, grid

Point = tuple[int, int]

BODY = 5          # segments behind the head
MAX_LOOP = 60.0   # seconds for one pass, at most
HEAD, TAIL = "#c084fc", "#7c3aed"


def route(goals: list[Point], start: Point = (0, 0)) -> tuple[list[Point], dict[Point, int]]:
    """Greedy nearest-goal walk in single-cell steps (horizontal first, then vertical).

    Returns (every position visited, step index at which each goal is eaten)."""
    path = [start]
    eaten: dict[Point, int] = {}
    left = set(goals)
    if start in left:
        eaten[start] = 0
        left.discard(start)
    x, y = start
    while left:
        gx, gy = min(left, key=lambda g: (abs(g[0] - x) + abs(g[1] - y), g[0], g[1]))
        while (x, y) != (gx, gy):
            if x != gx:
                x += 1 if gx > x else -1
            else:
                y += 1 if gy > y else -1
            path.append((x, y))
            if (x, y) in left:
                eaten[(x, y)] = len(path) - 1
                left.discard((x, y))
    return path, eaten


def board(ctx: BuildContext, x0: float, y0: float, pitch: int, cell: int, heat: tuple[str, ...]) -> str:
    """Heatmap cells (eaten ones fade to the empty colour) plus the animated snake on top."""
    cells = grid(ctx.data.weeks)
    goals = [(c.col, c.row) for c in cells if c.count > 0]
    path, eaten = route(goals)
    step = min(0.12, MAX_LOOP / max(1, len(path)))
    loop = len(path) * step + 1.5
    dur = f'dur="{loop:.2f}s" repeatCount="indefinite"'

    def rect(c: Cell) -> str:
        x, y = x0 + c.col * pitch, y0 + c.row * pitch
        color = heat[c.level]
        at = eaten.get((c.col, c.row))
        anim = (
            f'<animate attributeName="fill" values="{color};{heat[0]}" keyTimes="0;{at * step / loop:.4f}" '
            f'calcMode="discrete" {dur}/>'
            if at is not None else ""
        )
        return f'<rect x="{x:g}" y="{y:g}" width="{cell}" height="{cell}" rx="2.5" fill="{color}">{anim}</rect>'

    key_times = ";".join(f"{i * step / loop:.4f}" for i in range(len(path)))
    segments = []
    if len(path) > 1:
        for k in range(BODY, -1, -1):  # tail first so the head draws on top
            positions = ";".join(
                f"{x0 + p[0] * pitch:g},{y0 + p[1] * pitch:g}" for p in (path[max(0, i - k)] for i in range(len(path)))
            )
            size = cell if k == 0 else cell - 1 - k * 0.6
            inset = (cell - size) / 2
            segments.append(
                f'<g><animateTransform attributeName="transform" type="translate" values="{positions}" '
                f'keyTimes="{key_times}" calcMode="discrete" {dur}/>'
                f'<rect x="{inset:.1f}" y="{inset:.1f}" width="{size:.1f}" height="{size:.1f}" rx="3" '
                f'fill="{HEAD if k == 0 else TAIL}" opacity="{1 - k * 0.1:.2f}"/></g>'
            )
    return "".join(rect(c) for c in cells) + "".join(segments)
