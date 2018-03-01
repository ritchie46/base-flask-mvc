FROM nginx:1.13.9-alpine

RUN apk update && \
    apk add --no-cache bash

COPY nginx.conf /etc/nginx/nginx.conf
RUN rm /etc/nginx/conf.d/default.conf
COPY web.conf /etc/nginx/conf.d/