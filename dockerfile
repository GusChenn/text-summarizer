FROM alpine:latest
RUN apk update && apk add py-pip && apk add --no-cache python3-dev
RUN apk add make automake gcc g++ subversion gfortran
RUN pip install --upgrade pip
WORKDIR /app
COPY . /app
RUN pip --no-cache-dir install -r requirements.txt
CMD ["python3", "app.py"]