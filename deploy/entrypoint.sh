#!/bin/sh
# Substitute STARCLAW_PORT in supervisord template and start supervisord.
# Default port 8088; override at runtime with -e STARCLAW_PORT=3000.
set -e
export STARCLAW_PORT="${STARCLAW_PORT:-8088}"
envsubst '${STARCLAW_PORT}' \
  < /etc/supervisor/conf.d/supervisord.conf.template \
  > /etc/supervisor/conf.d/supervisord.conf
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
