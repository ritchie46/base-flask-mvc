FROM python:3.6.4-alpine3.7

COPY . /app
WORKDIR /app

# Need compiler and header file to build pip dependencies
RUN apk update && \
    apk add --no-cache --virtual build-deps gcc python-dev musl-dev libffi-dev && \
    apk add --no-cache postgresql-dev bash

# Remove redundant libs
RUN pip install  --no-cache-dir -r requirements.txt && apk del build-deps

## testing locally
#ENTRYPOINT ["python"]
#CMD ["gun   run.py"]