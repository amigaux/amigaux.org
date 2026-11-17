# amigaux.org

The site of amigaux, Amiga UNIX (Commodore's SVR4 for the Amiga) made easier to install and run
on newer Amiga hardware, and the server configuration for its package repository. Two host names:

- **`amigaux.org`**: the site, with the user documentation, downloads, news and the man pages.
- **`pkg.amigaux.org`**: the package repository (`catalog`, `catalog.md5`, `pkgs/…`), served over
  plain HTTP for `apkg`, with an HTTPS twin for browsers. The tree is written by the release
  tooling in the amix repository, never by hand.

| Path | What |
|------|------|
| `pages/` | The site's content in Markdown, one file per page |
| `theme/` | The MkDocs theme: templates, `site.css`, fonts, logo, icons, the man-page browser |
| `hooks/` | MkDocs hooks: `%NAME%` constants from `mkdocs.yml`, the preview mode |
| `mkdocs.yml`, `requirements.txt` | Site config and navigation; the pinned build dependencies |
| `tools/build.sh` | Builds into `build/site/` (gitignored), with the man pages when `MAN_PKGS` is set |
| `tools/check-site.py` | Refuses placeholders, third-party loads and broken internal links |
| `tools/man-*` | The man pages: collected from the release packages, formatted with a pinned mandoc |
| `deploy.sh` | Builds, checks and rsyncs `build/site/` to the docroot (`DEPLOY_HOST`, `DEPLOY_DEST`) |
| `server/` | Apache vhosts, `robots.txt`, the certbot hook, the stats timers, `install.sh` |
| `media/EMBED.md` | How the install demo clips were cut and embedded |
| `assets/src/` | The original artwork and logo concepts |

Build: `pip install -r requirements.txt`, then `tools/build.sh` (see its header for the man pages).

The site holds the user documentation; the [grimoire](https://grimoire.amigaux.org/) is the
deep reference.
