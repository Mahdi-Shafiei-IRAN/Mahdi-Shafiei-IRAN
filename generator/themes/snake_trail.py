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


def board(
    ctx: BuildContext,
    x0: float,
    y0: float,
    pitch: int,
    cell: int,
    heat: tuple[str, ...],
    *,
    head: str = HEAD,
    tail: str = TAIL,
) -> str:
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
        for k in range(BODY, 0, -1):  # tail first so the head draws on top
            positions = ";".join(
                f"{x0 + p[0] * pitch:g},{y0 + p[1] * pitch:g}" for p in (path[max(0, i - k)] for i in range(len(path)))
            )
            size = cell - 1 - k * 0.6
            inset = (cell - size) / 2
            segments.append(
                f'<g><animateTransform attributeName="transform" type="translate" values="{positions}" '
                f'keyTimes="{key_times}" calcMode="discrete" {dur}/>'
                f'<rect x="{inset:.1f}" y="{inset:.1f}" width="{size:.1f}" height="{size:.1f}" rx="3" '
                f'fill="{tail}" opacity="{1 - k * 0.1:.2f}"/></g>'
            )
        segments.append(_head(path, x0, y0, pitch, cell, key_times, dur, head))
    return "".join(rect(c) for c in cells) + "".join(segments)


def _head(
    path: list[Point], x0: float, y0: float, pitch: int, cell: int, key_times: str, dur: str, color: str
) -> str:
    """A slightly bigger head with a cute face: big eyes whose pupils look where the snake is going."""
    positions = ";".join(f"{x0 + p[0] * pitch:g},{y0 + p[1] * pitch:g}" for p in path)
    looks = ["1,0"] + [
        f"{(b[0] - a[0]) * 0.9:g},{(b[1] - a[1]) * 0.9:g}" for a, b in zip(path, path[1:])
    ]
    s = cell + 3                      # head is a bit larger than a cell
    o = -1.5                          # ...and centred on it
    eyes = "".join(
        f'<circle cx="{ex}" cy="4.6" r="2.4" fill="#fff"/>' for ex in (3.2, 7.8)
    )
    pupils = "".join(f'<circle cx="{ex}" cy="4.6" r="1.2" fill="#1e1b4b"/>' for ex in (3.2, 7.8))
    return (
        f'<g><animateTransform attributeName="transform" type="translate" values="{positions}" '
        f'keyTimes="{key_times}" calcMode="discrete" {dur}/>'
        f'<rect x="{o}" y="{o}" width="{s}" height="{s}" rx="5" fill="{color}"/>'
        f"{eyes}"
        f'<g><animateTransform attributeName="transform" type="translate" values="{";".join(looks)}" '
        f'keyTimes="{key_times}" calcMode="discrete" {dur}/>{pupils}</g>'
        '<circle cx="1.6" cy="8.4" r="1.1" fill="#f9a8d4" opacity=".9"/>'
        '<circle cx="9.4" cy="8.4" r="1.1" fill="#f9a8d4" opacity=".9"/>'
        '<path d="M4.4 8.6q1.1 1.2 2.2 0" fill="none" stroke="#1e1b4b" stroke-width=".8" stroke-linecap="round"/>'
        "</g>"
    )
