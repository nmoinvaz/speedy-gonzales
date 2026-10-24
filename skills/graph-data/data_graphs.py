"""Shared SVG drawing primitives for data graphs.

Canonical copy: skills/graph-data/data_graphs.py in
github.com/nmoinvaz/speedy-gonzales. Projects vendor this file next to their
graph scripts, edit the canonical copy and copy it back out rather than
changing a vendored one. Standard library only.

    from data_graphs import GRID, INK, SERIES, Svg, footnote, marker
"""

import math
import platform
import subprocess
import sys

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SOFT = "#52514e"
GRID = "#e7e6e2"
WARN = "#c98500"
# Categorical slots in fixed order, assigned by series position, never cycled.
# The neutral last slot is for a series of least interest, order inputs so.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
          "#e87ba4", "#008300", "#4a3aa7", "#e34948", "#a6339a", "#7a7668"]

# Dark-mode counterparts, the same hues re-stepped for the dark surface.
# Colors absent here keep their light value in both modes.
DARK = {
    SURFACE: "#201f1d",
    INK: "#e8e6e3",
    INK_SOFT: "#a8a49d",
    GRID: "#343230",
    WARN: "#d69a2d",
    "#eb6834": "#dd5c26",
    "#eda100": "#c08800",
    "#e87ba4": "#d1678f",
    "#4a3aa7": "#7263cf",
    "#a6339a": "#c257b5",
    "#7a7668": "#948e82",
}

SHAPES = ["circle", "square", "diamond", "triangle", "cross", "triangle-down"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt_speed(bps):
    if bps >= 1e9:
        return f"{bps / 1e9:.2f} GB/s"
    return f"{bps / 1e6:.0f} MB/s"


def fmt_bytes(n):
    if n >= 1048576:
        return f"{n // 1048576}M"
    if n >= 1024:
        return f"{n // 1024}K"
    return str(n)


def fmt_mem(b):
    if b >= 1048576:
        return f"{b / 1048576:.2f} MiB"
    return f"{b / 1024:.1f} KiB"


def fmt_pct(d):
    """Signed percentage change, the only way changes are presented."""
    # Adding zero turns a rounded -0.0 into 0.0
    return f"{round(d, 1) + 0.0:+.1f}%"


def pct(v, base):
    """Change from base to v as fmt_pct text, empty without a base."""
    return fmt_pct((v - base) / base * 100) if base else ""


def text_width(s, size=12):
    """Rough rendered width of s in system-ui at size px, for layout."""
    return len(s) * size * 0.58


class Svg:
    """Collects body elements; the height is decided at finish time.

    surface and dark_surface override the background for light and dark mode.
    Everything drawn in SURFACE, such as marker rings and segment gaps,
    follows the override, so draw with SURFACE and pass the colors here.
    """

    def __init__(self, width, surface=SURFACE, dark_surface=DARK[SURFACE]):
        self.w = width
        self.parts = []
        self.surface = surface
        self.dark_surface = dark_surface

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=12, fill=INK_SOFT, anchor="start", weight="normal",
             tabular=False):
        # Tabular figures keep numbers in a column aligned digit for digit
        num = ' font-variant-numeric="tabular-nums"' if tabular else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
                 f'text-anchor="{anchor}" font-weight="{weight}"{num}>{esc(s)}</text>')

    def line(self, x1, y1, x2, y2, stroke, width=1):
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{stroke}" stroke-width="{width}"/>')

    def finish(self, height):
        parts = self.parts
        dark = {**DARK, SURFACE: self.dark_surface}
        if self.surface != SURFACE:
            parts = [p.replace(f'"{SURFACE}"', f'"{self.surface}"') for p in parts]
            dark[self.surface] = dark.pop(SURFACE)
        # Attribute selectors outrank presentation attributes, so dark mode
        # swaps every themed color in place without touching the body markup.
        rules = "".join(f'[fill="{l}"]{{fill:{d}}}[stroke="{l}"]{{stroke:{d}}}'
                        for l, d in dark.items())
        header = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" '
            f'height="{height}" viewBox="0 0 {self.w} {height}" '
            f'font-family="system-ui, sans-serif">',
            f'<style>@media (prefers-color-scheme: dark){{{rules}}}</style>',
            f'<rect width="{self.w}" height="{height}" fill="{self.surface}"/>']
        return "\n".join(header + parts + ["</svg>"]) + "\n"


def marker(svg, shape, x, y, color, title):
    """11px marker with a 2px surface ring and a hover title."""
    r = 5.5
    ring = f'stroke="{SURFACE}" stroke-width="2"'
    if shape == "circle":
        body = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" {ring}/>'
    elif shape == "square":
        body = (f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r:.1f}" '
                f'height="{2 * r:.1f}" fill="{color}" {ring}/>')
    elif shape == "diamond":
        pts = f"{x:.1f},{y - r - 1:.1f} {x + r + 1:.1f},{y:.1f} {x:.1f},{y + r + 1:.1f} {x - r - 1:.1f},{y:.1f}"
        body = f'<polygon points="{pts}" fill="{color}" {ring}/>'
    elif shape == "triangle":
        pts = f"{x:.1f},{y - r - 1:.1f} {x + r + 1:.1f},{y + r:.1f} {x - r - 1:.1f},{y + r:.1f}"
        body = f'<polygon points="{pts}" fill="{color}" {ring}/>'
    elif shape == "cross":
        a, c = 2.2, r + 1
        pts = " ".join(f"{x + dx:.1f},{y + dy:.1f}" for dx, dy in (
            (-a, -c), (a, -c), (a, -a), (c, -a), (c, a), (a, a),
            (a, c), (-a, c), (-a, a), (-c, a), (-c, -a), (-a, -a)))
        body = f'<polygon points="{pts}" fill="{color}" {ring}/>'
    else:  # triangle-down
        pts = f"{x:.1f},{y + r + 1:.1f} {x + r + 1:.1f},{y - r:.1f} {x - r - 1:.1f},{y - r:.1f}"
        body = f'<polygon points="{pts}" fill="{color}" {ring}/>'
    svg.add(f"<g>{body}<title>{esc(title)}</title></g>")


def dodge_markers(series_pts, step=5.0, tol=3.0):
    """Spread markers that would sit on top of each other.

    series_pts maps a series index to {slot: (x, y)}. Series within tol
    pixels of the same y at a slot are moved step pixels apart, the lower
    series index to the left, so series sharing a value all stay visible.
    The lines keep the true x.
    """
    out = {i: dict(pts) for i, pts in series_pts.items()}
    slots = set().union(*(set(pts) for pts in series_pts.values())) if series_pts else set()
    for slot in slots:
        stacked = sorted((pts[slot][1], i) for i, pts in series_pts.items() if slot in pts)
        cluster = []
        for y, i in stacked:
            if cluster and y - cluster[-1][0] > tol:
                spread_cluster(out, slot, [c for _, c in cluster], step)
                cluster = []
            cluster.append((y, i))
        if cluster:
            spread_cluster(out, slot, [c for _, c in cluster], step)
    return out


def spread_cluster(out, slot, members, step):
    members = sorted(members)
    for q, i in enumerate(members):
        x, y = out[i][slot]
        out[i][slot] = (x + (q - (len(members) - 1) / 2) * step, y)


def better_arrow(svg, x1, y1, x2, y2, label="better"):
    """Semi-transparent direction-of-better hint with a label along the shaft,
    "better" for a corner of a two-axis chart, "faster" or "smaller" for one axis."""
    ln = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / ln, (y2 - y1) / ln
    head = (f"{x2:.1f},{y2:.1f} "
            f"{x2 - 9 * ux - 4 * uy:.1f},{y2 - 9 * uy + 4 * ux:.1f} "
            f"{x2 - 9 * ux + 4 * uy:.1f},{y2 - 9 * uy - 4 * ux:.1f}")
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    if ang > 90 or ang < -90:
        ang += 180  # keep the label reading left to right
    svg.add(f'<g opacity="0.35"><line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2 - 6 * ux:.1f}" '
            f'y2="{y2 - 6 * uy:.1f}" stroke="{INK_SOFT}" stroke-width="2"/>'
            f'<polygon points="{head}" fill="{INK_SOFT}"/>'
            f'<text x="{mx:.1f}" y="{my - 7:.1f}" font-size="11" fill="{INK_SOFT}" '
            f'text-anchor="middle" transform="rotate({ang:.1f} {mx:.1f} {my:.1f})">'
            f'{esc(label)}</text></g>')


def better_hint(svg, x, y, w, h, where="corner", label="better", reverse=False):
    """better_arrow placed against the plot box at (x, y, w, h).

    corner: diagonal up and right inside the top right of the plot, for
            charts where better is a corner (faster and smaller).
    axis:   horizontal, extending the x axis past its right end, for a
            horizontal measure on a plot with an x title. Leave about 80px
            of margin there.
    below:  horizontal under the left end of the box, for bar columns and
            timelines without an x title beneath them.
    right:  vertical in the margin right of the plot, for one vertical
            measure. Leave about 30px of margin there.
    inside: vertical inside the plot's right edge, when there's no margin
            and the top right of the plot is empty.
    reverse points the arrow the other way, for lower-is-better measures.
    """
    if where == "corner":
        pts = (x + w - 128, y + 82, x + w - 40, y + 24)
    elif where == "axis":
        pts = (x + w + 12, y + h, x + w + 76, y + h)
    elif where == "below":
        pts = (x, y + h + 14, x + 64, y + h + 14)
    elif where == "right":
        pts = (x + w + 18, y + 92, x + w + 18, y + 30)
    elif where == "inside":
        pts = (x + w - 14, y + 90, x + w - 14, y + 20)
    else:
        raise ValueError(f"unknown better_hint placement {where!r}")
    if reverse:
        pts = pts[2:] + pts[:2]
    better_arrow(svg, *pts, label=label)


def legend(svg, right, y, items):
    """Dots and labels right-aligned at right, items as (label, color)."""
    lx = right
    for label, color in reversed(items):
        svg.text(lx, y, label, size=11, fill=INK, anchor="end")
        lx -= text_width(label, 11) + 10
        svg.add(f'<circle cx="{lx:.1f}" cy="{y - 4}" r="4.5" fill="{color}"/>')
        lx -= 16


def caption(svg, x, y, title, sub):
    """Panel title and subtitle, returns the first content baseline."""
    svg.text(x, y, title, size=12, fill=INK)
    svg.text(x, y + 16, sub, size=10)
    return y + 46


def bar_path(x, y, w, h):
    """Horizontal bar with a 4px rounded data end, square at the baseline."""
    r = min(4, w / 2)
    return (f"M{x:.1f} {y:.1f} h{w - r:.1f} a{r} {r} 0 0 1 {r} {r} v{h - 2 * r:.1f} "
            f"a{r} {r} 0 0 1 {-r} {r} h{-(w - r):.1f} z")


def segment(svg, x0, x1, y, h, fill, tip, label=None, ink=INK, stroke=None, opacity=None):
    """A stacked or timeline segment with a 2px surface gap after it, labeled when it fits.

    label is a list of candidate texts, longest first, the first that fits is
    drawn. ink is the label color, pick it for contrast with fill, it doesn't
    change with the theme since it sits on the fill, not the surface.
    """
    w = x1 - x0
    if w < 0.5:
        return
    edge = ""
    if stroke:
        # Inset by half the stroke so the segment spans exactly its extent
        x0, w, y, h = x0 + 0.75, w - 1.5, y + 0.75, h - 1.5
        edge = f' stroke="{stroke}" stroke-width="1.5"'
    if opacity is not None:
        edge += f' fill-opacity="{opacity}"'
    svg.add(f'<rect x="{x0:.1f}" y="{y:.2f}" width="{max(w - 2, 0.5):.1f}" height="{h:.2f}" '
            f'rx="2" fill="{fill}"{edge}><title>{esc(tip)}</title></rect>')
    for text in label or []:
        if w - 2 > text_width(text, 10) + 10:
            svg.text(x0 + (w - 2) / 2, y + h / 2 + 3.5, text, size=10, fill=ink,
                     anchor="middle", tabular=True)
            break


class Axis:
    """Maps data values onto one pixel span, linear or log."""

    def __init__(self, lo, hi, p0, p1, log=False):
        if log and lo <= 0:
            raise ValueError("log axis needs positive values")
        self.lo, self.hi, self.p0, self.p1, self.log = lo, hi, p0, p1, log

    def __call__(self, v):
        f = math.log10 if self.log else float
        t = (f(v) - f(self.lo)) / ((f(self.hi) - f(self.lo)) or 1)
        return self.p0 + t * (self.p1 - self.p0)

    def ticks(self):
        if self.log:
            return nice_log_ticks(self.lo, self.hi)
        return nice_ticks(self.lo, self.hi)


def axes(svg, x, y, w, h, xaxis, yaxis, xlabel, ylabel, xfmt=str, yfmt=str):
    """Plot frame with gridlines, tick labels, and the two axis titles.

    Returns the (xmap, ymap) Axis pair for placing data. xaxis and yaxis are
    (lo, hi) or (lo, hi, "log"). The labels are required and should name the
    quantity and its unit, e.g. "compressed size (MiB)" or "throughput (MB/s)";
    an empty one raises so a chart can't ship with an unlabeled axis.
    """
    if not xlabel.strip() or not ylabel.strip():
        raise ValueError("both axes need a label naming the quantity and unit")
    xmap = Axis(xaxis[0], xaxis[1], x, x + w, log=xaxis[2:] == ("log",))
    ymap = Axis(yaxis[0], yaxis[1], y + h, y, log=yaxis[2:] == ("log",))
    for v in xmap.ticks():
        px = xmap(v)
        svg.line(px, y, px, y + h, GRID)
        svg.text(px, y + h + 15, xfmt(v), size=11, anchor="middle", tabular=True)
    widest = 0
    for v in ymap.ticks():
        py = ymap(v)
        svg.line(x, py, x + w, py, GRID)
        svg.text(x - 6, py + 4, yfmt(v), size=11, anchor="end", tabular=True)
        widest = max(widest, text_width(yfmt(v), 11))
    svg.line(x, y + h, x + w, y + h, INK_SOFT)
    svg.line(x, y, x, y + h, INK_SOFT)
    svg.text(x + w / 2, y + h + 34, xlabel, size=12, fill=INK, anchor="middle")
    # The y title clears the widest tick label, leave that much margin left of x
    lx, cy = x - widest - 18, y + h / 2
    svg.add(f'<text x="{lx:.1f}" y="{cy:.1f}" font-size="12" fill="{INK}" '
            f'text-anchor="middle" transform="rotate(-90 {lx:.1f} {cy:.1f})">'
            f'{esc(ylabel)}</text>')
    return xmap, ymap


def callout(svg, x, y, label, dx=24, dy=-24):
    """Mark a point of interest: a ring around it and a leader to a label.

    dx and dy place the label relative to the point, pick them so the label
    sits in empty space and doesn't cover other marks.
    """
    svg.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="none" '
            f'stroke="{INK}" stroke-width="1.5"/>')
    ln = math.hypot(dx, dy) or 1
    svg.line(x + 10 * dx / ln, y + 10 * dy / ln, x + dx, y + dy, INK)
    svg.text(x + dx + (4 if dx >= 0 else -4), y + dy + 4, label, size=11, fill=INK,
             anchor="start" if dx >= 0 else "end", weight="bold")


def nice_step(span, count=3):
    """Round 1, 2, or 5 step giving about count intervals over span."""
    raw = span / count
    mag = 10 ** math.floor(math.log10(raw))
    return next(m * mag for m in (1, 2, 5, 10) if m * mag >= raw)


def nice_ticks(lo, hi, n=5):
    """About n round-numbered ticks covering [lo, hi] on a linear axis."""
    if hi <= lo:
        return [lo]
    step = nice_step(hi - lo, n)
    v = math.ceil(lo / step - 1e-9) * step
    ticks = []
    while v <= hi + step * 1e-9:
        ticks.append(round(v, 12))
        v += step
    return ticks


def nice_log_ticks(lo, hi):
    # A range under a decade falls back to every integer multiple
    for mults in ((1, 2, 5), range(1, 10)):
        ticks = []
        e = math.floor(math.log10(lo))
        while 10 ** e <= hi * 1.001:
            for mult in mults:
                v = mult * 10 ** e
                if lo * 0.999 <= v <= hi * 1.001:
                    ticks.append(v)
            e += 1
        if len(ticks) >= 3:
            break
    return ticks


def host_specs():
    """CPU, RAM, and OS of this machine, empty when they can't be read."""
    if sys.platform == "darwin":
        try:
            brand = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
            mem = int(subprocess.check_output(
                ["sysctl", "-n", "hw.memsize"], text=True)) // (1024 ** 3)
            return f"{brand}, {mem} GB, macOS {platform.mac_ver()[0]}"
        except (subprocess.SubprocessError, OSError, ValueError):
            return ""
    if sys.platform.startswith("linux"):
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except OSError:
            pass
        return ""
    if sys.platform == "win32":
        try:
            import ctypes
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            brand = " ".join(winreg.QueryValueEx(key, "ProcessorNameString")[0].split())
            mem_kb = ctypes.c_ulonglong()
            ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(mem_kb))
            mem = int(mem_kb.value) // (1024 ** 2)
            build = sys.getwindowsversion().build
            release = "11" if build >= 22000 else platform.win32_ver()[0]
            return f"{brand}, {mem} GB, Windows {release} {platform.win32_ver()[1]}"
        except (OSError, ValueError, AttributeError):
            return ""
    return ""


def footnote(svg, sources, machine, warnings, body_bottom, repo_url=None):
    """Source, machine, warning, and repository lines below the body, returns the height.

    sources are short "name version" strings for each series' origin.
    """
    note = "  ·  ".join(sources + ([machine] if machine else []))
    two_lines = machine and len(note) > 155
    height = body_bottom + 28 + (14 if two_lines else 0) + (16 if warnings else 0)
    y = height - 12
    if two_lines:
        svg.text(16, y, machine, size=10)
        y -= 14
        svg.text(16, y, "  ·  ".join(sources), size=10)
    else:
        svg.text(16, y, note, size=10)

    # Warning badge above the footnote, never color alone
    if warnings:
        svg.text(16, y - 16, "⚠", size=10, fill=WARN)
        svg.text(30, y - 16, " · ".join(warnings), size=10)

    # Repository link on the bottom line
    if repo_url:
        svg.add(f'<a href="{repo_url}"><text x="{svg.w - 16}" y="{height - 12}" '
                f'font-size="10" fill="{INK_SOFT}" text-anchor="end" '
                f'text-decoration="underline">{esc(repo_url.removeprefix("https://"))}'
                f'</text></a>')
    return height
