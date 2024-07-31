FROM python:3.12.3-bookworm

RUN mkdir /workspace

COPY requirements.txt /workspace/

RUN pip install -r workspace/requirements.txt
RUN playwright install-deps
RUN playwright install chromium

COPY reminder_bot.py \
    messages.py \
    .env\
    urls.py \
    midpass_playwrights.py \
    neondb_client.py \
    __init__.py \
    /workspace/

WORKDIR /workspace


CMD ["python", "reminder_bot.py"]