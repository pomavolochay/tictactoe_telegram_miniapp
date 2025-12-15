FROM nginx:1.27-alpine

RUN apk add --no-cache gettext openssl inotify-tools

COPY default.conf.template /etc/nginx/templates/default.conf.template
COPY proxy.conf /etc/nginx/snippets/proxy.conf
COPY entrypoint.sh /entrypoint-nginx.sh

RUN chmod +x /entrypoint-nginx.sh

ENV DOMAIN=localhost

ENTRYPOINT ["/entrypoint-nginx.sh"]
