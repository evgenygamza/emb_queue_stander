FROM python:3.12.3-bookworm

RUN mkdir /workspace

COPY reminder_bot.py \
    locators.py \
    urls.py \
    update_queue_position.py \
    __init__.py \
    requirements.txt \
    /workspace/

WORKDIR /workspace

RUN pip install -r requirements.txt

CMD ["sleep","infinity"]