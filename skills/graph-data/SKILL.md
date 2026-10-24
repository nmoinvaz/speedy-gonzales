---
name: graph-data
description: House style and shared SVG primitives for data graphs rendered by Python scripts (benchmark results, comparisons, profiles, any chart a repo's scripts produce). Use before writing or changing a script that draws a chart, adding a graph to a repo, or when a repo has a vendored data_graphs.py.
---

# Data graphs

Graphs are self-contained SVGs written by standard-library-only Python scripts, no
matplotlib or other packages. They render on GitHub (READMEs, PR comments, gists) in both
light and dark mode.

## Shared primitives

`data_graphs.py` beside this file is the canonical copy of the drawing primitives: palette,
dark-mode map, `Svg`, `axes`, `marker`, `dodge_markers`, `better_hint`, `better_arrow`,
`callout`, `legend`, `caption`, `bar_path`, `segment`, `nice_step`, `nice_ticks`,
`nice_log_ticks`, `host_specs`, `footnote`, and number formatters (`pct`, `fmt_pct`, ...).

Every chart has these four things:

1. **SVG with light and dark mode.** Build it with `Svg` and colors from the module
   constants, `Svg.finish` adds the dark-mode swap.
2. **Labeled axes.** Draw the plot frame with `axes(...)`, which requires an x and y label
   naming the quantity and its unit ("throughput (MB/s)", "compressed size (MiB)") and
   returns the scales for placing data. Say "lower is better" in the label when an axis is
   inverted from the usual sense.
3. **A better/faster arrow.** Place it with `better_hint(svg, x, y, w, h, where)` using the
   same plot box passed to `axes`:
   - `"corner"`: diagonal at the top right inside the plot, when better is a corner
     (faster and smaller).
   - `"axis"`: horizontal, extending the x axis to the right, for a horizontal measure on
     a plot with an x title. Needs about 80px of right margin.
   - `"below"`: horizontal under the left end, for bar columns and timelines with no x
     title beneath them.
   - `"right"`: vertical in the margin right of the plot, for one vertical measure. Needs
     about 30px of right margin.
   - `"inside"`: vertical inside the plot's right edge, when there's no margin and that
     corner of the plot is empty.

   Pass `label="faster"` or `"smaller"` to name the measure and `reverse=True` when lower
   is better. Mark an arrow whose meaning needs a caveat with an asterisk
   (`label="better*"`) and explain it in the panel subtitle. Use `better_arrow` with
   explicit coordinates only when none of the placements fit.
4. **Points of interest marked.** Use `callout` to ring and label what the reader should
   notice: the regression, the winner, the crossover, the default setting.

- Vendor it into the repo's scripts directory as `data_graphs.py`, unchanged, and import
  from it. Never copy individual functions into a graph script.
- A change to a primitive goes into the canonical copy first, then gets copied out to every
  repo that vendors it. If a vendored copy differs from the canonical one, reconcile them
  before editing either.
- Data loading, row parsing, and panel layout are specific to each repo and stay in its own
  scripts. Only drawing primitives used by more than one repo belong in `data_graphs.py`.

## Color

- Series take `SERIES` slots by position in a fixed order. Never cycle the palette, never
  pick colors by hand. More series than slots means the chart needs splitting.
- The last slot is neutral gray, for the series of least interest (a baseline, the
  reference build). Order inputs so it lands there.
- The default background is `SURFACE`, `#201f1d` in dark mode. A repo that needs another
  one passes it to `Svg(width, surface=..., dark_surface=...)` rather than editing the
  constants, e.g. solsta-bench's slate `dark_surface="#15171a"`. Keep drawing rings and
  gaps in `SURFACE`, they follow the override.
- Only use colors from the module constants. Any new themed color needs a `DARK` entry, or
  it keeps its light value in dark mode.
- Dark mode comes from the `<style>` block `Svg.finish` writes, which rewrites fill and
  stroke attributes by value. Don't use CSS classes or inline `style=` for colors, the swap
  can't reach them.

## Marks

- Markers are 11px with a 2px surface ring and a `<title>` so hovering shows the exact
  value. Use `marker`, and a second variable gets a shape from `SHAPES`, not another color.
- Run point series through `dodge_markers` so equal values stay visible.
- Use log axes (`(lo, hi, "log")` in `axes`) for values spanning more than about 10x.
- Keep callouts few, two or three per chart, or nothing stands out.

## Text and numbers

- Numbers that line up in columns (tick labels, table cells, values beside bars) use
  `tabular=True` on `Svg.text`.
- Text drawn on a colored fill (segment labels) takes a fixed ink chosen for contrast with
  that fill, it doesn't follow the theme.

- Show changes as signed percentages (`fmt_pct`, e.g. -18.4%), never speedup ratios
  (1.23x).
- Every graph ends with `footnote`: what produced each series (name and version or commit),
  the machine specs from `host_specs` plus anything the data records, and the repository
  link.
- Conditions that make the numbers suspect (high load, CPU scaling, debug builds, noisy
  rows above 3% CV, skipped inputs) go in the footnote's warnings, which draws a ⚠ badge.
  Never signal a warning by color alone.
- Scripts that draw a graph also print the same numbers as a table on stdout.

## Checking a graph

Open the SVG in a browser in both light and dark mode before committing it, and check that
labels don't collide and every series has a legend entry or direct label.
