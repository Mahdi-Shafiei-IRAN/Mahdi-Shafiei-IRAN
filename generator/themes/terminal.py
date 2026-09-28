"""Terminal theme: a neofetch-style window that types itself out."""

from __future__ import annotations

import pyfiglet

from ..components import Palette, image, link_assets, links_html, page, project_assets, projects_html
from ..context import BuildContext
from ..svg import MONO, WIDTH, compact, document, esc, grid, truncate
from .base import ThemeOutput

NAME = "terminal"
TITLE = "Terminal"

BG, BAR, BORDER = "#0d1117", "#161b22", "#30363d"
TEXT, MUTED = "#c9d1d9", "#8b949e"
GREEN, BLUE, YELLOW = "#3fb950", "#58a6ff", "#e3b341"
HEAT = ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353")
SWATCHES = ("#f85149", "#e3b341", "#3fb950", "#39c5cf", "#58a6ff", "#bc8cff", "#c9d1d9", "#6e7681")
PALETTE = Palette(bg=BG, border=BORDER, text=TEXT, muted=MUTED, accent=GREEN, font=MONO, radius=8)

FONT = 14
CHAR = FONT * 0.6
LINE = 21
LOGO_LINE = 15
PAD = 26
TYPE = 0.06  # seconds per typed character

STYLE = (
    f"text{{font-family:{MONO};font-size:{FONT}px;white-space:pre}}"
    ".o{opacity:0;animation:show .3s ease-out forwards}"
    "@keyframes show{to{opacity:1}}"
    ".cur{animation:blink 1.1s steps(1) infinite}"
    "@keyframes blink{50%{fill-opacity:0}}"
)


class Screen:
    """Lays out prompt lines and output blocks top to bottom, tracking y and the animation clock."""

    def __init__(self, user: str):
        self.user = user
        self.y = 70.0
        self.t = 0.5
        self.parts: list[str] = []
        self.defs: list[str] = []
        self._typed = 0

    @property
    def prompt_width(self) -> float:
        return (len(self.user) + len("@github:~$ ")) * CHAR

    def prompt(self) -> str:
        return (
            f'<tspan fill="{GREEN}" font-weight="700">{esc(self.user)}@github</tspan>'
            f'<tspan fill="{TEXT}">:</tspan><tspan fill="{BLUE}">~</tspan>'
            f'<tspan fill="{TEXT}">$ </tspan>'
        )

    def reveal(self, markup: str, at: float) -> None:
        self.parts.append(f'<g class="o" style="animation-delay:{at:.2f}s">{markup}</g>')

    def command(self, cmd: str) -> None:
        """Show the prompt, then type `cmd` after it one character at a time."""
        self._typed += 1
        widths = ";".join(f"{self.prompt_width + i * CHAR + 4:.1f}" for i in range(len(cmd) + 1))
        duration = (len(cmd) + 1) * TYPE
        self.defs.append(
            f'<clipPath id="type{self._typed}"><rect x="{PAD - 2}" y="{self.y - 16:.1f}" '
            f'width="{self.prompt_width + 4:.1f}" height="22">'
            f'<animate attributeName="width" values="{widths}" dur="{duration:.2f}s" '
            f'begin="{self.t:.2f}s" calcMode="discrete" fill="freeze"/></rect></clipPath>'
        )
        self.reveal(
            f'<text x="{PAD}" y="{self.y:.1f}" clip-path="url(#type{self._typed})">'
            f"{self.prompt()}{esc(cmd)}</text>",
            self.t - 0.3,
        )
        self.t += duration + 0.35
        self.y += LINE

    def block(self, markup: str, height: float) -> None:
        self.reveal(markup, self.t)
        self.y += height
        self.t += 0.35

    def cursor(self) -> None:
        self.reveal(
            f'<text x="{PAD}" y="{self.y:.1f}">{self.prompt()}<tspan class="cur" fill="{GREEN}">█</tspan></text>',
            self.t - 0.3,
        )
        self.y += LINE


def _info(ctx: BuildContext) -> list[tuple[str, str]]:
    p, d = ctx.profile, ctx.data
    rows = [
        ("Name", p.name),
        ("Role", p.role),
        ("Location", p.location),
        ("Repos", str(d.public_repos)),
        ("Stars", compact(d.stars)),
        ("Followers", compact(d.followers)),
        ("Commits", f"{d.total_contributions:,} in the last year"),
        ("Languages", ", ".join(lang.name for lang in d.languages[:3])),
        ("Learning", ", ".join(p.learning)),
    ]
    return [(k, v) for k, v in rows if v]


def _neofetch(s: Screen, ctx: BuildContext) -> None:
    logo = [line.rstrip() for line in pyfiglet.figlet_format(ctx.profile.initials, font="ansi_shadow").splitlines()]
    while logo and not logo[-1].strip():
        logo.pop()
    logo_w = max(map(len, logo)) * CHAR
    top = s.y
    s.defs.append(
        f'<linearGradient id="logo" gradientUnits="userSpaceOnUse" x1="{PAD}" y1="{top - 14:.1f}" '
        f'x2="{PAD + logo_w:.1f}" y2="{top + len(logo) * LOGO_LINE:.1f}">'
        f'<stop offset="0" stop-color="{GREEN}"/><stop offset=".5" stop-color="#39c5cf"/>'
        f'<stop offset="1" stop-color="#bc8cff"/></linearGradient>'
    )
    s.reveal(
        "".join(
            f'<text x="{PAD}" y="{top + i * LOGO_LINE:.1f}" fill="url(#logo)" xml:space="preserve">{esc(line)}</text>'
            for i, line in enumerate(logo)
        ),
        s.t,
    )

    x = PAD + logo_w + 40
    room = int((WIDTH - PAD - x) / CHAR)
    title = f"{s.user}@github"
    rows = [
        f'<tspan fill="{GREEN}" font-weight="700">{esc(s.user)}</tspan><tspan fill="{TEXT}">@</tspan>'
        f'<tspan fill="{BLUE}" font-weight="700">github</tspan>',
        f'<tspan fill="{MUTED}">{"-" * len(title)}</tspan>',
    ]
    for key, value in _info(ctx):
        rows.append(
            f'<tspan fill="{BLUE}" font-weight="700">{esc(key)}</tspan><tspan fill="{MUTED}">: </tspan>'
            f"{esc(truncate(value, room - len(key) - 2))}"
        )
    for i, row in enumerate(rows):
        s.reveal(f'<text x="{x:.1f}" y="{top + i * LINE:.1f}">{row}</text>', s.t + 0.08 * i)
    sy = top + len(rows) * LINE - 12
    s.reveal(
        "".join(
            f'<rect x="{x + i * 3 * CHAR:.1f}" y="{sy:.1f}" width="{3 * CHAR:.1f}" height="16" fill="{c}"/>'
            for i, c in enumerate(SWATCHES)
        ),
        s.t + 0.08 * len(rows),
    )
    s.y += max(len(logo) * LOGO_LINE, (len(rows) + 1) * LINE) + 14
    s.t += 0.08 * (len(rows) + 1) + 0.4


def _projects(s: Screen, ctx: BuildContext) -> None:
    s.command("ls ~/projects")
    if not ctx.data.featured:
        s.block(f'<text x="{PAD}" y="{s.y:.1f}" fill="{MUTED}">(nothing pinned yet)</text>', LINE + 8)
        return
    x, y, items = float(PAD), s.y, []
    for repo in ctx.data.featured:
        name = repo.name + "/"
        width = len(name) * CHAR
        if x > PAD and x + width > WIDTH - PAD:
            x, y = float(PAD), y + LINE
        items.append(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{repo.language_color}" font-weight="700">{esc(name)}</text>'
        )
        x += width + 3 * CHAR
    s.block("".join(items), y - s.y + LINE + 8)


def _heatmap(s: Screen, ctx: BuildContext) -> None:
    s.command("contributions --last-year")
    pitch, size = 13, 10
    top = s.y - 12
    columns: dict[int, list[str]] = {}
    for c in grid(ctx.data.weeks):
        columns.setdefault(c.col, []).append(
            f'<rect x="{PAD + c.col * pitch}" y="{top + c.row * pitch:.1f}" width="{size}" '
            f'height="{size}" rx="2" fill="{HEAT[c.level]}"/>'
        )
    for col, rects in columns.items():
        s.reveal("".join(rects), s.t + col * 0.015)
    label_y = top + 7 * pitch + 20
    legend_x = WIDTH - PAD - 5 * pitch - 4 * CHAR
    legend = "".join(
        f'<rect x="{legend_x + i * pitch:.1f}" y="{label_y - 10:.1f}" width="{size}" height="{size}" '
        f'rx="2" fill="{color}"/>'
        for i, color in enumerate(HEAT)
    )
    s.reveal(
        f'<text x="{PAD}" y="{label_y:.1f}" fill="{MUTED}">'
        f"{ctx.data.total_contributions:,} contributions in the last year</text>"
        f'<text x="{legend_x - 5 * CHAR:.1f}" y="{label_y:.1f}" fill="{MUTED}">Less</text>{legend}'
        f'<text x="{legend_x + 5 * pitch + 4:.1f}" y="{label_y:.1f}" fill="{MUTED}">More</text>',
        s.t + 0.8,
    )
    s.y = label_y + LINE + 10
    s.t += 1.3


def _frame(height: float, title: str) -> str:
    return (
        f'<rect x=".5" y=".5" width="{WIDTH - 1}" height="{height - 1:g}" rx="12" fill="{BG}" stroke="{BORDER}"/>'
        f'<path d="M1 12.5A11.5 11.5 0 0 1 12.5 1h{WIDTH - 25}A11.5 11.5 0 0 1 {WIDTH - 1} 12.5V38H1z" fill="{BAR}"/>'
        f'<path d="M1 38.5h{WIDTH - 2}" stroke="{BORDER}"/>'
        f'<circle cx="22" cy="19.5" r="6" fill="#ff5f57"/><circle cx="42" cy="19.5" r="6" fill="#febc2e"/>'
        f'<circle cx="62" cy="19.5" r="6" fill="#28c840"/>'
        f'<text x="{WIDTH / 2:g}" y="24" text-anchor="middle" font-size="13" fill="{MUTED}">{esc(title)}</text>'
    )


def terminal_svg(ctx: BuildContext) -> str:
    s = Screen(ctx.profile.first_name.lower())
    s.command("neofetch")
    _neofetch(s, ctx)
    if ctx.profile.tagline:
        s.command("echo $MOTTO")
        room = int((WIDTH - 2 * PAD) / CHAR)
        s.block(
            f'<text x="{PAD}" y="{s.y:.1f}" fill="{YELLOW}">{esc(truncate(ctx.profile.tagline, room))}</text>',
            LINE + 8,
        )
    _projects(s, ctx)
    _heatmap(s, ctx)
    s.cursor()
    height = round(s.y + 4)
    return document(
        WIDTH,
        height,
        _frame(height, f"{s.user}@github: ~") + f'<g fill="{TEXT}">' + "".join(s.parts) + "</g>",
        title=f"{ctx.profile.name}: terminal profile",
        style=STYLE,
        defs="".join(s.defs),
    )


def build(ctx: BuildContext) -> ThemeOutput:
    featured = ctx.data.featured
    assets = {
        "terminal.svg": terminal_svg(ctx),
        **project_assets(featured, PALETTE, prefix="~/"),
        **link_assets(ctx.profile, PALETTE),
    }

    def readme(prefix: str) -> str:
        return page(
            image(prefix, "terminal.svg", f"{ctx.profile.name}: terminal profile"),
            projects_html(featured, prefix),
            links_html(ctx.profile, prefix),
        )

    return ThemeOutput(assets, readme)
