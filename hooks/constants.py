"""MkDocs hook: fill %NAME% tokens in the Markdown pages from mkdocs.yml extra.constants.

URLs that will move (the grimoire, the support repository) are written once, in
mkdocs.yml, and pages use the token. A %NAME% with no constant stops the build,
so a typo never reaches the site. Only upper-case names between % signs are
tokens; "100%" and the like are left alone.
"""
import re

from mkdocs.exceptions import PluginError

TOKEN = re.compile(r"%([A-Z][A-Z0-9_]*)%")


def on_page_markdown(markdown, page, config, files):
    constants = config.extra.get("constants", {})

    def fill(m):
        name = m.group(1)
        if name not in constants:
            raise PluginError(f"{page.file.src_path}: unknown constant %{name}%")
        return str(constants[name])

    return TOKEN.sub(fill, markdown)
