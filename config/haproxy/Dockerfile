# FROM mtksitap54:5000/haproxy:1.7
FROM haproxy:1.8

# RUN apt-get update --no-install-recommends \
# 	&& apt-get install -y net-tools curl 
RUN mkdir -p /var/log/nginx && touch /var/log/nginx/access.log \
    && touch /var/log/nginx/error.log \
    && ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log \
    && mkdir /my_to_do_static \
    && groupadd haproxy \
    && useradd -g haproxy haproxy

COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

EXPOSE 80 5678 5566