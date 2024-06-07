FROM python:3.12.3-bookworm

RUN mkdir /workspace

COPY reminder_bot.py \
    locators.py \
    urls.py \
    midpass_playwrights.py \
    neondb_client.py \
    __init__.py \
    requirements.txt \
    /workspace/

WORKDIR /workspace

RUN pip install -r requirements.txt
RUN playwright install chromium
RUN pip install "python-telegram-bot[job-queue]"
RUN playwright install-deps

CMD ["python", "reminder_bot.py"]