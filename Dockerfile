#
FROM python:3.9

WORKDIR /game-club-website

COPY ./requirements.txt /game-club-website/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /game-club-website/requirements.txt

COPY ./app /game-club-website/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
