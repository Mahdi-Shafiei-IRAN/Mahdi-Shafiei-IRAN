"""Space Shooter theme: a ship flies under the contribution graph and blasts every active day."""

from __future__ import annotations

from ..components import Palette, image, link_assets, links_html, page, project_assets, projects_html
from ..context import BuildContext
from ..svg import MONO, WIDTH, Cell, compact, document, esc, grid, rng, truncate
from .base import ThemeOutput

NAME = "space-shooter"
TITLE = "Space Shooter"

SPACE, PANEL, BORDER = "#05060f", "#0a0f1f", "#1e293b"
TEXT, MUTED = "#e2e8f0", "#7c8aa5"
CYAN, LIME, MAGENTA = "#22d3ee", "#a3e635", "#f472b6"
ENEMY = ("#111827", "#4c1d95", "#7e22ce", "#c026d3", "#f0abfc")
PALETTE = Palette(bg=PANEL, border=BORDER, text=TEXT, muted=MUTED, accent=CYAN, font=MONO, radius=6)

PITCH, CELL = 14, 11
GRID_X, GRID_Y = (WIDTH - 53 * PITCH) // 2, 48
SHIP_Y = 228
GAME_H = 266
MAX_LOOP = 60.0  # seconds for one full pass
MIN_TARGETS = 10
GHOSTS = 24


def targets(ctx: BuildContext) -> tuple[list[Cell], list[Cell]]:
    """(real targets, ghost targets). Ghosts only appear on a quiet graph so the game still plays."""
    cells = grid(ctx.data.weeks)
    real = [c for c in cells if c.count > 0]
    ghosts: list[Cell] = []
    if len(real) < MIN_TARGETS:
        empty = [c for c in cells if c.count == 0]
        ghosts = rng(ctx.day.isoformat()).sample(empty, min(GHOSTS, len(empty)))
    order = sorted(real + ghosts, key=lambda c: (c.col, -c.row))
    ghost_set = set(ghosts)
    return [c for c in order if c not in ghost_set], [c for c in order if c in ghost_set]


def _cx(cell: Cell) -> float:
    return GRID_X + cell.col * PITCH + CELL / 2


def _cy(cell: Cell) -> float:
    return GRID_Y + cell.row * PITCH + CELL / 2


def _t(seconds: float, loop: float) -> str:
    return f"{min(seconds / loop, 1):.4f}"


def game_svg(ctx: BuildContext) -> str:
    real, ghosts = targets(ctx)
    ordered = sorted(real + ghosts, key=lambda c: (c.col, -c.row))
    step = min(0.35, MAX_LOOP / max(1, len(ordered)))
    loop = len(ordered) * step + 2.0

    stars = []
    r = rng("space-stars")
    for _ in range(70):
        stars.append(
            f'<circle cx="{r.uniform(0, WIDTH):.0f}" cy="{r.uniform(0, GAME_H):.0f}" r="{r.uniform(.4, 1.4):.1f}" '
            f'fill="#fff" style="animation:twinkle {r.uniform(2, 5):.1f}s ease-in-out -{r.uniform(0, 5):.1f}s infinite"/>'
        )

    ghost_set = set(ghosts)
    hit_at = {cell: i * step + step * 0.6 for i, cell in enumerate(ordered)}
    board = []
    for cell in grid(ctx.data.weeks):
        x, y = GRID_X + cell.col * PITCH, GRID_Y + cell.row * PITCH
        if cell in hit_at:
            hit = hit_at[cell]
            fade = (
                f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{_t(hit, loop)};'
                f'{_t(hit + 0.12, loop)};1" dur="{loop:.2f}s" repeatCount="indefinite"/>'
            )
            boom = (
                f'<circle cx="{x + CELL / 2}" cy="{y + CELL / 2}" r="0" fill="none" stroke="{LIME}" stroke-width="2">'
                f'<animate attributeName="r" values="0;0;11;11" keyTimes="0;{_t(hit, loop)};'
                f'{_t(hit + 0.3, loop)};1" dur="{loop:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;{_t(hit, loop)};'
                f'{_t(hit + 0.3, loop)};1" dur="{loop:.2f}s" repeatCount="indefinite"/></circle>'
            )
            if cell in ghost_set:
                board.append(
                    f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="none" stroke="{MAGENTA}" '
                    f'stroke-dasharray="2 2">{fade}</rect>{boom}'
                )
            else:
                board.append(
                    f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{ENEMY[cell.level]}">'
                    f"{fade}</rect>{boom}"
                )
        else:
            board.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{ENEMY[0]}"/>')

    # ship path: glide to each target's column, fire once it arrives
    xs, move_times, laser_y2, laser_ops, laser_times = [], [], [], [], []
    prev_x = WIDTH / 2
    for i, cell in enumerate(ordered):
        start, arrive = i * step, i * step + step * 0.45
        xs += [f"{prev_x:.1f},0", f"{_cx(cell):.1f},0"]
        move_times += [start, arrive]
        laser_y2.append(f"{_cy(cell) - SHIP_Y:.1f}")
        laser_times += [arrive, hit_at[cell]]
        laser_ops += ["1", "0"]
        prev_x = _cx(cell)
    xs += [f"{prev_x:.1f},0", f"{WIDTH / 2:.1f},0"]
    move_times += [len(ordered) * step, loop]
    if ordered:
        ship_anim = (
            f'<animateTransform attributeName="transform" type="translate" values="{";".join(xs)}" '
            f'keyTimes="{";".join(_t(t, loop) for t in move_times)}" '
            f'dur="{loop:.2f}s" repeatCount="indefinite"/>'
        )
        laser = (
            f'<line x1="0" y1="-14" x2="0" y2="-14" stroke="{LIME}" stroke-width="2" stroke-linecap="round" opacity="0">'
            f'<animate attributeName="y2" values="{";".join(laser_y2)}" '
            f'keyTimes="{";".join(_t(i * step, loop) for i in range(len(ordered)))}" dur="{loop:.2f}s" '
            'calcMode="discrete" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;{";".join(laser_ops)}" '
            f'keyTimes="0;{";".join(_t(t, loop) for t in laser_times)}" dur="{loop:.2f}s" '
            'calcMode="discrete" repeatCount="indefinite"/></line>'
        )
    else:
        ship_anim, laser = "", ""
    ship = (
        f'<g transform="translate({WIDTH / 2} 0)">{ship_anim}<g transform="translate(0 {SHIP_Y})">{laser}'
        f'<path class="flame" d="M-5 10 L0 {22} L5 10z" fill="{MAGENTA}"/>'
        f'<path d="M0 -16 L7 -2 L16 6 L16 11 L5 8 L0 12 L-5 8 L-16 11 L-16 6 L-7 -2z" fill="{CYAN}" '
        f'stroke="#e0f2fe" stroke-width="1"/><circle cx="0" cy="-3" r="2.6" fill="{SPACE}"/></g></g>'
    )
    year = ctx.data.weeks[-1][-1].date[:4] if ctx.data.weeks and ctx.data.weeks[-1] else ""
    hud = (
        f'<text x="{GRID_X}" y="30" font-size="12" letter-spacing="2" fill="{CYAN}">SECTOR {esc(year)} // '
        f"CONTRIBUTION FIELD</text>"
        f'<text x="{WIDTH - GRID_X}" y="30" text-anchor="end" font-size="12" letter-spacing="2" fill="{MUTED}">'
        f"TARGETS {len(real)}{f' + {len(ghosts)} DRILL' if ghosts else ''}</text>"
    )
    style = (
        f"text{{font-family:{MONO}}}"
        "@keyframes twinkle{50%{opacity:.2}}"
        ".flame{transform-box:fill-box;transform-origin:top;animation:flame .18s ease-in-out infinite alternate}"
        "@keyframes flame{to{transform:scaleY(.55)}}"
    )
    body = (
        f'<rect width="{WIDTH}" height="{GAME_H}" rx="14" fill="{SPACE}"/>'
        f'{"".join(stars)}{hud}{"".join(board)}{ship}'
        f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{GAME_H - 1}" rx="14" fill="none" stroke="{BORDER}"/>'
    )
    return document(WIDTH, GAME_H, body, title=f"{ctx.profile.name}: space shooter contribution graph", style=style)


def telemetry_svg(ctx: BuildContext) -> str:
    p, d = ctx.profile, ctx.data
    engine = f"{d.languages[0].name} {d.languages[0].percent:g}%" if d.languages else "warming up"
    rows = [
        ("PILOT", p.name),
        ("CLASS", p.role),
        ("SCORE", f"{d.total_contributions:,} contributions"),
        ("FLEET", f"{d.public_repos} repositories"),
        ("STARS", compact(d.stars)),
        ("SHIELDS", f"{compact(d.followers)} followers"),
        ("ENGINE", engine),
    ]
    h = 56 + len(rows) * 22
    lines = [
        f'<text x="28" y="36" font-size="13" font-weight="700" fill="{CYAN}">&gt; TELEMETRY_LINK ESTABLISHED'
        f'<tspan class="blink" fill="{LIME}"> _</tspan></text>'
    ]
    for i, (key, value) in enumerate(rows):
        lines.append(
            f'<text class="row" style="animation-delay:{0.3 + i * 0.18:.2f}s" x="28" y="{66 + i * 22}" font-size="13">'
            f'<tspan fill="{MUTED}">{key.ljust(9, ".")}</tspan><tspan fill="{TEXT}"> {esc(truncate(value, 52))}</tspan>'
            "</text>"
        )
    cx, cy, radius = WIDTH - 110, h / 2, 62
    radar = (
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{LIME}" stroke-opacity=".35"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{radius * .62:.0f}" fill="none" stroke="{LIME}" stroke-opacity=".25"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{radius * .25:.0f}" fill="none" stroke="{LIME}" stroke-opacity=".2"/>'
        f'<path d="M{cx - radius} {cy}h{2 * radius}M{cx} {cy - radius}v{2 * radius}" stroke="{LIME}" stroke-opacity=".2"/>'
        f'<g class="sweep"><path d="M{cx} {cy}L{cx} {cy - radius}A{radius} {radius} 0 0 1 '
        f'{cx + radius * .7:.1f} {cy - radius * .714:.1f}z" fill="url(#beam)"/></g>'
        f'<circle class="blip" cx="{cx + 24}" cy="{cy - 18}" r="3" fill="{MAGENTA}"/>'
        f'<circle class="blip" style="animation-delay:1.1s" cx="{cx - 30}" cy="{cy + 20}" r="3" fill="{CYAN}"/>'
    )
    defs = (
        f'<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{LIME}" '
        f'stop-opacity=".05"/><stop offset="1" stop-color="{LIME}" stop-opacity=".45"/></linearGradient>'
    )
    corners = "".join(
        f'<path d="M{x} {y + 16 * sy}v{-16 * sy}h{16 * sx}" fill="none" stroke="{CYAN}" stroke-width="2"/>'
        for x, y, sx, sy in ((8, 8, 1, 1), (WIDTH - 8, 8, -1, 1), (8, h - 8, 1, -1), (WIDTH - 8, h - 8, -1, -1))
    )
    style = (
        f"text{{font-family:{MONO};white-space:pre}}"
        ".row{opacity:0;animation:row .4s steps(4) forwards}@keyframes row{to{opacity:1}}"
        ".blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{fill-opacity:0}}"
        f".sweep{{transform-origin:{cx}px {cy}px;animation:spin 3s linear infinite}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        ".blip{opacity:0;animation:blip 3s ease-out infinite}@keyframes blip{10%{opacity:1}60%,to{opacity:0}}"
    )
    body = (
        f'<rect width="{WIDTH}" height="{h}" rx="10" fill="{PANEL}"/>{corners}'
        + "".join(lines)
        + radar
    )
    return document(WIDTH, h, body, title="Pilot telemetry", style=style, defs=defs)


def build(ctx: BuildContext) -> ThemeOutput:
    featured = ctx.data.featured
    assets = {
        "game.svg": game_svg(ctx),
        "telemetry.svg": telemetry_svg(ctx),
        **project_assets(featured, PALETTE, prefix="» "),
        **link_assets(ctx.profile, PALETTE),
    }

    def readme(prefix: str) -> str:
        return page(
            image(prefix, "game.svg", f"{ctx.profile.name}: space shooter contribution graph"),
            image(prefix, "telemetry.svg", "Pilot telemetry"),
            projects_html(featured, prefix),
            links_html(ctx.profile, prefix),
        )

    return ThemeOutput(assets, readme)
