import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from user_consts import BOT_TOKEN, MAIL, PASSWORD
from update_queue_position import Midpass

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def update_queue_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_ID = update.effective_chat.id

    await context.bot.send_message(chat_id=CHAT_ID, text="Захожу в кабинет")
    
    script = Midpass()
    login_status = script.login_private_person(mail=MAIL, password=PASSWORD)
    await context.bot.send_message(chat_id=CHAT_ID, text=f"{login_status[1]}")
    if not login_status[0]:
        return
    position = script.go_to_waiting_list_and_check_position()
    await context.bot.send_message(chat_id=CHAT_ID, text=f"Текущее место в очереди: {position}")
    if position < 100:
        await context.bot.send_message(chat_id=CHAT_ID, text="Внимание! \n Осталось меньше ста человек")
    result_message = script.update_queue_position()
    await context.bot.send_message(chat_id=CHAT_ID, text=result_message)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    queue_update_handler = CommandHandler('queue', update_queue_position)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(queue_update_handler)
    application.add_handler(echo_handler)
    
    application.run_polling()
    