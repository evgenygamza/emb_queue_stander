import logging
import datetime

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
    chat_id = update.effective_chat.id

    await context.bot.send_message(chat_id=chat_id, text="Захожу в кабинет")
    with NeonConnect(dsn=DB_CONNECTION, chat_id=chat_id) as db_client:
        user_info = db_client.fetch_user_info()
        script = Midpass()
        login_status = script.login_private_person(mail=user_info[1], password=user_info[2])
        await context.bot.send_message(chat_id=chat_id, text=f"{login_status[1]}")
        if not login_status[0]:
            await context.bot.send_message(chat_id=chat_id,
                                           text=f"Авторизация по каким-то причинам не удалась. Давайте попробуем ещё")
        elif login_status[0] == "banned":
            context.job_queue.run_once(reminder, when=3600, chat_id=chat_id, name="banned_case")

        pstn = script.go_to_waiting_list_and_check_position()
        await context.bot.send_message(chat_id=chat_id, text=f"Текущее место в очереди: {pstn}")
        db_client.update(position=pstn)

        if pstn < 100:
            await context.bot.send_message(chat_id=chat_id, text="Внимание! \n Осталось меньше ста человек")
        result_message = script.update_queue_position()
        await context.bot.send_message(chat_id=chat_id, text=result_message)


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


async def reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    message_text = ("Пора подтвердить место в очереди. \n"
                    "Пожалуйста, отправь мне команду /queue")
    await context.bot.send_message(job.chat_id, message_text)


async def daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    with NeonConnect(dsn=DB_CONNECTION) as db:
        chat_ids = db.fetch_chat_ids()
    for chat_id in chat_ids:
        context.job_queue.run_once(reminder, when=1, chat_id=chat_id, name=str(chat_id))


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    job_queue = application.job_queue

    job_queue.run_daily(daily_reminder, time=datetime.time(hour=8, minute=3))

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

    application.add_handlers([start_handler, help_handler, queue_update_handler, get_position_handler])
    application.add_handlers([new_password_handler, new_email_handler])
    application.add_handler(delete_handler)
    application.add_handler(echo_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
