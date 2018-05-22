# FROM mtksitap54:5000/tekn0ir/nginx-stream
FROM tekn0ir/nginx-stream

# RUN apt-get update --no-install-recommends \
# && apt-get install -y net-tools curl 
RUN mkdir -p /var/log/nginx && touch /var/log/nginx/access.log \
    && touch /var/log/nginx/error.log \
    && ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log \
    && mkdir /my_to_do_static
COPY ./nginx.conf /opt/nginx/http.conf.d

#host static
COPY ./static /my_to_do_static/static

EXPOSE 8888