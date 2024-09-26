FROM rabbitmq-python-base:0.0.1

COPY consumer.py /root/consumer.py
CMD /root/consumer.py