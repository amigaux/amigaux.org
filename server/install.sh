#!/bin/bash
# Install or refresh the amigaux.org + pkg.amigaux.org server config on the
# web host.  Idempotent; safe to re-run after editing the vhost files.
#
#   rsync -a server/ "$DEPLOY_HOST:amigaux-server/"
#   ssh "$DEPLOY_HOST" sudo DEPLOY_USER=<user> amigaux-server/install.sh
#
#   DEPLOY_USER   required: the account deploy.sh rsyncs as (no root needed);
#                 it owns the docroots and runs the stats timer
#   GROUP         the web server's group (default www-data)
#   SERVER_DIR    where server/ was copied on the host (default: this
#                 script's directory); the systemd units run the scripts there
#
# Does NOT issue certificates (certbot --webroot, once, by hand) and never
# touches any other vhost on the host.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEPLOY_USER="${DEPLOY_USER:?install.sh: set DEPLOY_USER, the deploy account}"
SERVER_DIR="${SERVER_DIR:-$HERE}"
GROUP="${GROUP:-www-data}"

[[ $EUID -eq 0 ]] || { echo "install.sh: run with sudo" >&2; exit 1; }

echo "== docroots"
for d in amigaux.org pkg.amigaux.org; do
    install -d -o "$DEPLOY_USER" -g "$GROUP" -m 755 "/var/www/$d"
done
install -o "$DEPLOY_USER" -g "$GROUP" -m 644 "$HERE/robots.txt" /var/www/pkg.amigaux.org/robots.txt

echo "== apache vhosts"
for v in amigaux.org pkg.amigaux.org; do
    install -m 644 "$HERE/apache/$v.conf" "/etc/apache2/sites-available/$v.conf"
done
a2enmod -q ssl rewrite
a2ensite -q amigaux.org pkg.amigaux.org

echo "== stats timer"
install -d -o "$DEPLOY_USER" -g "$DEPLOY_USER" -m 755 /var/www/amigaux.org/stats
# The units carry @DEPLOY_USER@ and @SERVER_DIR@; they are filled in here.
for u in amigaux-stats.service amigaux-stats.timer amigaux-geoip.service amigaux-geoip.timer; do
    sed -e "s|@DEPLOY_USER@|$DEPLOY_USER|g" -e "s|@SERVER_DIR@|$SERVER_DIR|g" "$HERE/systemd/$u" \
        > "/etc/systemd/system/$u"
    chmod 644 "/etc/systemd/system/$u"
done
systemctl daemon-reload
systemctl enable --now amigaux-stats.timer
systemctl enable --now amigaux-geoip.timer

echo "== certbot deploy hook"
install -d /etc/letsencrypt/renewal-hooks/deploy
install -m 755 "$HERE/renewal-hooks/reload-apache.sh" /etc/letsencrypt/renewal-hooks/deploy/reload-apache.sh

echo "== configtest + reload"
apache2ctl configtest
systemctl reload apache2
echo "install.sh: done"
