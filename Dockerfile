FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/user && chmod 777 /app/user

ENV web_port=8080
ENV api_host=0.0.0.0

EXPOSE 8080

CMD ["bash", "run-web.sh"]
