"""MkDocs hook: the preview build (tools/build.sh --preview).

extra.preview is "1" in the preview build and empty otherwise; extra.base is the site's
path on the server, "/" or "/preview/". In the preview every PLACEHOLDER marker is shown
as TBD: the pages are a public draft, and tools/check-site.py --preview counts them.
A normal build leaves the markers in place, so check-site still refuses them there.
"""
from mkdocs.exceptions import PluginError


def on_config(config):
    extra = config.extra
    extra["preview"] = str(extra.get("preview", "")).strip().lower() in ("1", "true", "yes")
    base = str(extra.get("base", "/"))
    if not (base.startswith("/") and base.endswith("/")):
        raise PluginError(f"extra.base must start and end with '/': {base!r}")
    extra["base"] = base
    return config


def on_page_content(html, page, config, files):
    if config.extra["preview"]:
        return html.replace("PLACEHOLDER", "TBD")
    return html
