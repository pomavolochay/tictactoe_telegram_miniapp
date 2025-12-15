#!/bin/sh
set -euo pipefail

TEMPLATE=/etc/nginx/templates/default.conf.template
NGINX_CONF=/etc/nginx/conf.d/default.conf
SNIPPET=/etc/nginx/snippets/live-cert.conf
DUMMY_DIR=/etc/nginx/ssl/dummy
LIVE_DIR="/etc/letsencrypt/live/${DOMAIN}"
CERTBOT_ROOT=/var/www/certbot

render_config() {
  mkdir -p "$(dirname "$NGINX_CONF")"
  envsubst '$DOMAIN' < "$TEMPLATE" > "$NGINX_CONF"
}

write_snippet() {
  cert_path="$1"
  key_path="$2"
  cat > "$SNIPPET" <<EOF
ssl_certificate     $cert_path;
ssl_certificate_key $key_path;
ssl_protocols       TLSv1.2 TLSv1.3;
ssl_session_cache   shared:SSL:50m;
ssl_session_timeout 1d;
EOF
}

ensure_dummy_cert() {
  mkdir -p "$DUMMY_DIR"
  if [ ! -f "$DUMMY_DIR/fullchain.pem" ] || [ ! -f "$DUMMY_DIR/privkey.pem" ]; then
    openssl req -x509 -nodes -days 3 -newkey rsa:2048 \
      -keyout "$DUMMY_DIR/privkey.pem" \
      -out "$DUMMY_DIR/fullchain.pem" \
      -subj "/CN=${DOMAIN:-localhost}"
  fi
  write_snippet "$DUMMY_DIR/fullchain.pem" "$DUMMY_DIR/privkey.pem"
}

use_live_cert_if_available() {
  if [ -f "$LIVE_DIR/fullchain.pem" ] && [ -f "$LIVE_DIR/privkey.pem" ]; then
    current_target=$(cat "$SNIPPET" 2>/dev/null || true)
    if printf '%s' "$current_target" | grep -F "$LIVE_DIR" >/dev/null 2>&1; then
      return 1
    fi
    write_snippet "$LIVE_DIR/fullchain.pem" "$LIVE_DIR/privkey.pem"
    return 0
  fi
  return 1
}

render_config
mkdir -p "$CERTBOT_ROOT" /etc/nginx/snippets

if ! use_live_cert_if_available; then
  ensure_dummy_cert
fi

watch_for_real_cert() {
  while true; do
    if use_live_cert_if_available; then
      nginx -s reload || true
    fi
    sleep 300 &
    wait $!
  done
}

watch_for_real_cert &

exec nginx -g "daemon off;"
