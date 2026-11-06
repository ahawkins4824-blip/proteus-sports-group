"""Small inline SVG icons shared by the Proteus website templates."""

from html import escape


PATHS = {
    'arrow-up-right': '<path d="M5 19 19 5M5 5h14v14"/>',
    'arrow-right': '<path d="M4 12h16m-6-6 6 6-6 6"/>',
    'arrow-left': '<path d="M20 12H4m6-6-6 6 6 6"/>',
    'arrow-down': '<path d="M12 4v16m-6-6 6 6 6-6"/>',
    'play': '<path d="m7 4 14 8-14 8Z" fill="currentColor" stroke="none"/>',
    'pause': '<path d="M7 5h3v14H7Zm7 0h3v14h-3Z" fill="currentColor" stroke="none"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'close': '<path d="m6 6 12 12M6 18 18 6"/>',
    'asterisk': '<path d="M12 2v20M2 12h20M5 5l14 14M5 19 19 5"/>',
}


def icon(name, *, data_icon=None, hidden=False):
    """Render decorative vector artwork without relying on platform glyphs."""
    artwork = PATHS[name]
    data = f' data-icon="{escape(data_icon, quote=True)}"' if data_icon else ''
    visibility = ' hidden' if hidden else ''
    return (
        f'<svg class="icon icon-{name}" viewBox="0 0 24 24" '
        f'aria-hidden="true" focusable="false" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"{data}{visibility}>'
        f'{artwork}</svg>'
    )
