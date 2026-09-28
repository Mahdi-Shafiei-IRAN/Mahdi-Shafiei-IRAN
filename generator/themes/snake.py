"""Snake theme: an arcade scoreboard, then a snake that eats its way through the contribution graph."""

from __future__ import annotations

from ..components import Palette, image, link_assets, links_html, page, project_assets, projects_html
from ..context import BuildContext
from ..svg import MONO, WIDTH, Cell, compact, document, esc, grid, rng
from .base import ThemeOutput

NAME = "snake"
TITLE = "Snake Trail"

BG, PANEL, BORDER = "#0d1117", "#161b22", "#30363d"
TEXT, MUTED = "#e6edf3", "#8b949e"
GREEN, PURPLE, INDIGO, AMBER = "#39d353", "#a855f7", "#6366f1", "#f2cc60"
HEAT = ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353")
PALETTE = Palette(bg=PANEL, border=BORDER, text=TEXT, muted=MUTED, accent=GREEN, font=MONO, radius=8)

PITCH, CELL = 14, 11
GRID_X, GRID_Y = (WIDTH - 53 * PITCH) // 2, 44
SNAKE_H = 160
BODY = 5           # segments behind the head
MAX_LOOP = 60.0
MIN_TARGETS = 10
GHOSTS = 24

Point = tuple[int, int]


def targets(ctx: BuildContext) -> tuple[list[Cell], set[Cell]]:
    """Active days, plus seeded ghost cells when the graph is too quiet to play."""
    cells = grid(ctx.data.weeks)
    real = [c for c in cells if c.count > 0]
    ghosts: set[Cell] = set()
    if len(real) < MIN_TARGETS:
        empty = [c for c in cells if c.count == 0]
        ghosts = set(rng(ctx.day.isoformat()).sample(empty, min(GHOSTS, len(empty))))
    return real + sorted(ghosts, key=lambda c: (c.col, c.row)), ghosts


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


def _xy(p: Point) -> str:
    return f"{GRID_X + p[0] * PITCH},{GRID_Y + p[1] * PITCH}"


def snake_svg(ctx: BuildContext) -> str:
    goals, ghosts = targets(ctx)
    by_point = {(c.col, c.row): c for c in goals}
    path, eaten = route(list(by_point))
    step = min(0.12, MAX_LOOP / max(1, len(path)))
    loop = len(path) * step + 1.5
    key_times = ";".join(f"{i * step / loop:.4f}" for i in range(len(path)))

    cells = []
    for cell in grid(ctx.data.weeks):
        x, y = GRID_X + cell.col * PITCH, GRID_Y + cell.row * PITCH
        point = (cell.col, cell.row)
        if point in eaten and cell in ghosts:
            at = eaten[point] * step / loop
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="none" stroke="{AMBER}" '
                f'stroke-dasharray="2 2"><animate attributeName="opacity" values="1;0" keyTimes="0;{at:.4f}" '
                f'dur="{loop:.2f}s" calcMode="discrete" repeatCount="indefinite"/></rect>'
            )
        elif point in eaten:
            at = eaten[point] * step / loop
            color = HEAT[cell.level]
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}">'
                f'<animate attributeName="fill" values="{color};{HEAT[0]}" keyTimes="0;{at:.4f}" '
                f'dur="{loop:.2f}s" calcMode="discrete" repeatCount="indefinite"/></rect>'
            )
        else:
            cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{HEAT[0]}"/>')

    segments = []
    for k in range(BODY, -1, -1):  # tail first so the head draws on top
        positions = ";".join(_xy(path[max(0, i - k)]) for i in range(len(path)))
        color = PURPLE if k == 0 else INDIGO
        size = CELL if k == 0 else CELL - 1 - k * 0.6
        inset = (CELL - size) / 2
        segments.append(
            f'<g><animateTransform attributeName="transform" type="translate" values="{positions}" '
            f'keyTimes="{key_times}" dur="{loop:.2f}s" calcMode="discrete" repeatCount="indefinite"/>'
            f'<rect x="{inset:.1f}" y="{inset:.1f}" width="{size:.1f}" height="{size:.1f}" rx="3" fill="{color}" '
            f'opacity="{1 - k * 0.1:.2f}"/></g>'
        )
    body = (
        f'<rect width="{WIDTH}" height="{SNAKE_H}" rx="12" fill="{BG}" stroke="{BORDER}"/>'
        f'<text x="{GRID_X}" y="28" font-size="12" letter-spacing="2" fill="{MUTED}">'
        f"LEVEL 1 · {len(goals) - len(ghosts)} FRUITS"
        f"{f' · {len(ghosts)} PRACTICE' if ghosts else ''}</text>"
        f'<text x="{WIDTH - GRID_X}" y="28" text-anchor="end" font-size="12" letter-spacing="2" fill="{GREEN}">'
        "▶ PLAYING</text>"
        + "".join(cells)
        + "".join(segments)
    )
    style = f"text{{font-family:{MONO}}}"
    return document(WIDTH, SNAKE_H, body, title=f"{ctx.profile.name}: snake eating the contribution graph", style=style)


def scoreboard_svg(ctx: BuildContext) -> str:
    p, d = ctx.profile, ctx.data
    scores = (
        ("SCORE", f"{d.total_contributions:,}"),
        ("LENGTH", str(d.active_days)),
        ("REPOS", str(d.public_repos)),
        ("STARS", compact(d.stars)),
    )
    h = 150
    parts = [
        f'<text x="{WIDTH / 2:g}" y="40" text-anchor="middle" font-size="13" letter-spacing="4" fill="{AMBER}">'
        f"PLAYER 1 · {esc(p.name.upper())}</text>",
        f'<text x="{WIDTH / 2:g}" y="62" text-anchor="middle" font-size="12" fill="{MUTED}">{esc(p.role)}</text>',
    ]
    w = WIDTH / 4
    for i, (label, value) in enumerate(scores):
        cx = w * i + w / 2
        parts.append(
            f'<text x="{cx:.0f}" y="104" text-anchor="middle" font-size="28" font-weight="700" fill="{GREEN}" '
            f'filter="url(#neon)">{esc(value)}</text>'
            f'<text x="{cx:.0f}" y="128" text-anchor="middle" font-size="11" letter-spacing="3" fill="{MUTED}">'
            f"{label}</text>"
        )
    defs = (
        '<filter id="neon" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="3" '
        'result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    )
    style = (
        f"text{{font-family:{MONO}}}"
        ".blink{animation:blink 1.2s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    )
    body = (
        f'<rect width="{WIDTH}" height="{h}" rx="12" fill="{BG}" stroke="{BORDER}"/>'
        f'<text class="blink" x="24" y="30" font-size="11" letter-spacing="2" fill="{PURPLE}">● REC</text>'
        f'<text x="{WIDTH - 24}" y="30" text-anchor="end" font-size="11" letter-spacing="2" fill="{MUTED}">'
        f"HI-SCORE {compact(d.followers)} FOLLOWERS</text>"
        + "".join(parts)
    )
    return document(WIDTH, h, body, title="Arcade scoreboard", style=style, defs=defs)


def build(ctx: BuildContext) -> ThemeOutput:
    featured = ctx.data.featured
    assets = {
        "scoreboard.svg": scoreboard_svg(ctx),
        "snake.svg": snake_svg(ctx),
        **project_assets(featured, PALETTE),
        **link_assets(ctx.profile, PALETTE),
    }

    def readme(prefix: str) -> str:
        return page(
            image(prefix, "scoreboard.svg", "Arcade scoreboard"),
            image(prefix, "snake.svg", f"{ctx.profile.name}: snake eating the contribution graph"),
            projects_html(featured, prefix),
            links_html(ctx.profile, prefix),
        )

    return ThemeOutput(assets, readme)
