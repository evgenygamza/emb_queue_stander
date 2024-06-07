FROM python:3.12.3-bookworm

RUN mkdir /workspace

COPY reminder_bot.py \
    locators.py \
    user_consts.py \
    urls.py \
    midpass_playwrights.py \
    neondb_client.py \
    __init__.py \
    requirements.txt \
    /workspace/

WORKDIR /workspace

RUN pip install -r requirements.txt
RUN playwright install-deps
RUN playwright install chromium

CMD ["python", "reminder_bot.py"]