#!/bin/sh
# certbot deploy hook: the amigaux.org cert is issued with --webroot (no
# installer), so Apache must be told to pick up the renewed files.
exec systemctl reload apache2
