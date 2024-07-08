FROM python:3.10-slim

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3", "./main.py" ]

# CMD ["sh", "-c", "pip3 install -r requirements.txt"]

