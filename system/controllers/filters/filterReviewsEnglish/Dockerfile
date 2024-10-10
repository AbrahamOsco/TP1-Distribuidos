FROM system:latest
RUN pip install pika langid
COPY system/controllers/filters/filterReviewsEnglish /app/system/controllers/filters/filterReviewsEnglish
ENTRYPOINT ["/bin/sh"]

