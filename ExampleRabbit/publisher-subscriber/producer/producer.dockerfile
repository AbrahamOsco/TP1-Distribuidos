FROM rabbitmq-python-base:0.0.1

COPY producer.py /root/producer.py
CMD /root/producer.py