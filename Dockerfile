FROM python:3.13.2

WORKDIR /app/bot
COPY requirements.txt /app/bot
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/bot

CMD ["python", "-m", "bot"]