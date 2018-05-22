#FROM mtksitap54:5000/python:3.6.2
FROM python:3.6.2

RUN export http_proxy=http://172.23.29.23:3128 && apt-get update --no-install-recommends \
 && apt-get install -y net-tools curl alien vim libaio-dev libsasl2-dev libldap2-dev libssl-dev
RUN rm -rf /var/lib/apt/lists/* && mkdir /mytodo

COPY ./config/deploy/oracle-instantclient12.2-basic-12.2.0.1.0-1.x86_64.rpm /tmp/oracle-instantclient12.2-basic-12.2.0.1.0-1.x86_64.rpm
RUN alien -i /tmp/oracle-instantclient12.2-basic-12.2.0.1.0-1.x86_64.rpm && rm /tmp/oracle-instantclient12.2-basic-12.2.0.1.0-1.x86_64.rpm \
&& cp /usr/lib/oracle/12.2/client64/lib/libclntsh.so.12.1 /usr/lib/oracle/12.2/client64/lib/libclntsh.so

ENV LD_LIBRARY_PATH=/usr/lib/oracle/12.2/client64/lib
ENV DJANGO_SETTINGS_MODULE=my_to_do.settings_prod
EXPOSE 8080 5678
WORKDIR /mytodo
COPY ./requirements.txt /mytodo/requirements.txt
RUN pip install --proxy http://172.23.29.23:3128 setuptools_scm
RUN pip install --proxy http://172.23.29.23:3128 -r requirements.txt

COPY . /mytodo
RUN rm /mytodo/config/deploy/*.rpm
CMD ["fab", "start_gunicorn"]

