"""The one place that decides what a figure of this project looks like.

Every module that draws calls use_figure_style() before it draws, and nothing sets a
matplotlib rcParam anywhere else. Two modules used to set the font at *module level*,
which meant importing them changed the font of every figure drawn afterwards anywhere in
the process - so whether the web interface's own charts came out in the project font
depended on whether a derived input had happened to be missing that session, and the same
chart looked different from one run to the next.

Applied per call rather than once at import for the same reason: a module that changes
global state as a side effect of being imported is a module whose effect depends on import
order. Calling it is cheap - rcParams is a dict - and it is idempotent.

The font is asked for by name. If it is not installed, matplotlib falls back and says so
once rather than per figure; the fallback list below keeps that fallback a serif rather
than whatever the default happens to be, so a figure without Times New Roman still looks
like the rest of them.
"""

FONT_FAMILY = 'Times New Roman'
FONT_FALLBACKS = ['Times New Roman', 'Times', 'DejaVu Serif', 'serif']

# Every time-of-day axis in the project is labelled on this grid: a clock reading every
# two hours. Two rather than one because the schedule figures are 48 columns wide and a
# label per hour crowds them; two rather than four because a reader looking for "what
# happened at 14:00" should not have to count cells from the nearest tick.
HOUR_TICK_STRIDE = 2
# The unit those labels carry, written the way an axis label writes a unit everywhere else
# in this project - in square brackets after the quantity.
TIME_AXIS_LABEL = 'Time of day [hh:mm]'


def hhmm(hours):
    """A clock label for a time-of-day axis: 6.5 -> '06:30', 24 -> '24:00'.

    The end of the day is '24:00' and not '00:00'. Both name the same instant and only one
    of them says which end of the figure it is on; the model's own step_to_time formats it
    the same way, so the grids and the curves agree on what the last tick is called.
    """
    total_minutes = int(round(float(hours) * 60))
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"

# every figure is written as PNG. A raster keeps the browser fast: the Streamlit page lays
# the figures out again on every interaction, and a vector plot of a dense schedule costs
# it thousands of DOM nodes each time. 150 dpi so the raster still holds up when zoomed.
FIGURE_DPI = 150

_warned = False


def use_figure_style(plt):
    """Apply the project's figure style to `plt`. Idempotent; safe to call per figure."""
    global _warned
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = FONT_FALLBACKS
    # STIX is the one math fontset matplotlib ships that was drawn to Times' metrics, so a
    # unit in an axis label and an exponent in it are the same typeface and not two.
    plt.rcParams['mathtext.fontset'] = 'stix'
    if not _warned:
        _warned = True
        try:
            from matplotlib.font_manager import findfont, FontProperties, get_font
            # findfont raises on a family that is genuinely absent, which is the signal
            # wanted here. What it returns is then confirmed against the family name stored
            # *inside* the file rather than against the file's name: Times New Roman ships
            # as times.ttf, so matching the family against the path would announce the font
            # as missing on every machine that has it.
            found = findfont(FontProperties(family=FONT_FAMILY), fallback_to_default=False)
            if get_font(found).family_name != FONT_FAMILY:
                raise ValueError(found)
        except Exception:
            print(f"note: '{FONT_FAMILY}' is not installed; figures fall back to "
                  f"{FONT_FALLBACKS[1]} or the default serif.", flush=True)
    return plt