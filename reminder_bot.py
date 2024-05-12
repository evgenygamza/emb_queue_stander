import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import apscheduler as sched

from telegram import Update
from telegram.ext import (filters, ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler,
                          MessageHandler, CallbackContext)
from user_consts import BOT_TOKEN, DB_CONNECTION, MAIL, PASSWORD
from update_queue_position import Midpass
from neondb_client import NeonConnect

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

GET_PASSWORD, GET_EMAIL = 0, 1
# scheduler = AsyncIOScheduler()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_ID = update.effective_chat.id
    message = "\
        Список команд:\n\
        - /queue - Подтвердить заявку\n\
        - /position - Узнать своё текущее место в очереди\n\
        - /email - ввести свою почту\n\
        - /password - обновить пароль\n\
        - /cancel - отменить ввод пароля или почты\n\
        - /delete - удалить свои данные\n\
        - /start или /help - повторить эту инструкцию\n\
            "
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    with NeonConnect(dsn=DB_CONNECTION, chat_id=CHAT_ID) as db_client:
        user_exists = db_client.check_user_exists()
        if not user_exists:
            db_client.add_user()


async def update_queue_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_ID = update.effective_chat.id

    await context.bot.send_message(chat_id=CHAT_ID, text="Захожу в кабинет")
    with NeonConnect(dsn=DB_CONNECTION, chat_id=CHAT_ID) as db_client:
        user_info = db_client.fetch_user_info()
        script = Midpass()
        login_status = script.login_private_person(mail=user_info[1], password=user_info[2])
        await context.bot.send_message(chat_id=CHAT_ID, text=f"{login_status[1]}")
        if not login_status[0]:
            await context.bot.send_message(chat_id=CHAT_ID,
                                           text=f"Авторизация по каким-то причинам не удалась. Давайте попробуем ещё")

        pstn = script.go_to_waiting_list_and_check_position()
        await context.bot.send_message(chat_id=CHAT_ID, text=f"Текущее место в очереди: {pstn}")
        db_client.update(position=pstn)

        if pstn < 100:
            await context.bot.send_message(chat_id=CHAT_ID, text="Внимание! \n Осталось меньше ста человек")
        result_message = script.update_queue_position()
        await context.bot.send_message(chat_id=CHAT_ID, text=result_message)


async def get_user_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_ID = update.effective_chat.id
    with NeonConnect(dsn=DB_CONNECTION, chat_id=CHAT_ID) as db_client:
        pos = db_client.fetch_user_info('position')[0]
    await context.bot.send_message(chat_id=CHAT_ID, text=f"С последнего обновления ваш номер был {pos}")


async def new_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_ID = update.effective_chat.id
    await context.bot.send_message(chat_id=CHAT_ID, text="Введите в следующем сообщении пароль:")
    return GET_PASSWORD


async def get_new_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_ID = update.effective_chat.id
    new_passw = update.message.text
    with NeonConnect(dsn=DB_CONNECTION, chat_id=CHAT_ID) as db_client:
        new_passw_from_db = db_client.update(passw=new_passw)
    await context.bot.send_message(chat_id=CHAT_ID, text=f"Новый пароль: {new_passw_from_db}")


async def new_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_ID = update.effective_chat.id
    await context.bot.send_message(chat_id=CHAT_ID, text="Введите в следующем сообщении адрес электронной почты:")
    return GET_EMAIL


async def get_new_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_ID = update.effective_chat.id
    new_email = update.message.text
    with NeonConnect(dsn=DB_CONNECTION, chat_id=CHAT_ID) as db_client:
        new_email_from_db = db_client.update(email=new_email)
    await context.bot.send_message(chat_id=CHAT_ID, text=f"Новая почта: {new_email_from_db}")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Действие отменено")
    return ConversationHandler.END


async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_ID = update.effective_chat.id
    with NeonConnect(dsn=DB_CONNECTION, chat_id=CHAT_ID) as db_client:
        user_exists = db_client.check_user_exists()
        if user_exists:
            try:
                db_client.delete_user_info()
                user_exists = db_client.check_user_exists()
            except:
                await context.bot.send_message(chat_id=CHAT_ID, text="Что-то пошло не так. Попробуйте еще раз: /delete")
        if not user_exists:
            await context.bot.send_message(chat_id=CHAT_ID, text="Удалено")


# @scheduler.scheduled_job('cron', id='reminder_msg', minute='*', jitter=1)
# @scheduler.scheduled_job('cron', id='reminder_msg', hour=5, minute=30)
# async def reminds(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # CHAT_ID = update.effective_chat.id
#     # CHAT_ID = update.effective_chat.id
#     with NeonConnect(dsn=DB_CONNECTION, chat_id=208605587) as db_client:
#         chat_ids = db_client.fetch_user_info("chat_id")  # Замените на реальные идентификаторы
#         await context.bot.send_message(chat_id=CHAT_ID, text="Думаю, пора обновить своё место в очереди.\n"
#     #     # for chat_id in chat_ids:
#     #         # await context.bot.send_message(chat_id=chat_id, text="Думаю, пора обновить своё место в очереди.\n"
#                                                                  "Выполни команду /queue")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', start)
    queue_update_handler = CommandHandler('queue', update_queue_position)
    get_position_handler = CommandHandler('position', get_user_position)
    new_password_handler = ConversationHandler(
        entry_points=[CommandHandler('password', new_password)],
        states={GET_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_new_password)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    new_email_handler = ConversationHandler(
        entry_points=[CommandHandler('email', new_email)],
        states={GET_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_new_email)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    delete_handler = CommandHandler('delete', delete_user)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    # application.job_queue.run_daily(reminds, time=datetime.strptime('16:29', '%H:%M').time(), days=(0, 1, 2, 3, 4))

    application.add_handlers([start_handler, help_handler, queue_update_handler, get_position_handler])
    application.add_handlers([new_password_handler, new_email_handler])
    application.add_handler(delete_handler)
    application.add_handler(echo_handler)

    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(reminds, 'interval', seconds=5, args=[application.bot, None])
    # scheduler.add_job(reminds, 'cron', minute='*', jitter=1)

    # scheduler.start()
    application.run_polling()


if __name__ == '__main__':
    main()
