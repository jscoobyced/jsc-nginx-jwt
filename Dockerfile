ARG ALPINE_VERSION=3.22.1

FROM alpine:${ALPINE_VERSION} AS nginx

### builder ###
FROM nginx AS builder

# Install dependencies
WORKDIR /build
RUN apk --no-cache upgrade
RUN apk --no-cache add curl gcc gd-dev geoip-dev jansson-dev libxslt-dev \
    linux-headers make musl-dev nginx openssl-dev pcre-dev perl-dev \
    zlib-dev unzip

RUN echo "NGINX_VERSION=$(nginx -v 2>&1 | sed 's/^[^0-9]*//')" > /build/.env
RUN source /build/.env && echo "Nginx version ${NGINX_VERSION}"

# Download nginx-auth-jwt
RUN curl -sL -o nginx-auth-jwt.zip https://github.com/kjdev/nginx-auth-jwt/archive/refs/heads/main.zip
RUN unzip nginx-auth-jwt.zip
WORKDIR /build/nginx-auth-jwt-main

# Download nginx
RUN source /build/.env && curl -sL -o nginx-${NGINX_VERSION}.tar.gz http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz
RUN source /build/.env && tar -xf nginx-${NGINX_VERSION}.tar.gz
RUN source /build/.env && mv nginx-${NGINX_VERSION} nginx
WORKDIR /build/nginx-auth-jwt-main/nginx

RUN nginx_opt=$(nginx -V 2>&1 | tail -1 | sed -e "s/configure arguments://" -e "s| --add-dynamic-module=[^ ]*||g") \
    && ./configure ${nginx_opt} --add-dynamic-module=../ --with-cc-opt='-DNGX_HTTP_HEADERS'
RUN make
RUN mkdir -p /usr/lib/nginx/modules
RUN cp objs/ngx_http_auth_jwt_module.so /usr/lib/nginx/modules/
RUN mkdir -p /etc/nginx/modules
RUN echo 'load_module "/usr/lib/nginx/modules/ngx_http_auth_jwt_module.so";' > /etc/nginx/modules/auth_jwt.conf
RUN nginx -t

### nginx ###
FROM nginx

RUN apk --no-cache upgrade
RUN apk --no-cache add jansson nginx

COPY --from=builder /usr/lib/nginx/modules/ngx_http_auth_jwt_module.so /usr/lib/nginx/modules/ngx_http_auth_jwt_module.so
COPY --from=builder /etc/nginx/modules/auth_jwt.conf /etc/nginx/modules/auth_jwt.conf
RUN echo "include /etc/nginx/conf.d/*.conf;" > /etc/nginx/nginx.conf

CMD [ "nginx"]