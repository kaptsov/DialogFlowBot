import logging
from functools import partial

from environs import Env
from telegram import Update, ForceReply
from telegram.ext import \
    Updater, \
    CallbackContext, \
    CommandHandler, \
    MessageHandler, \
    Filters

from dialogflow import detect_intent_texts


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_html(
        rf"Здравствуйте, {user.mention_html()}! Давайте пообщаемся.",
        reply_markup=ForceReply(selective=True),
    )


def help(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
        text="Для обучения бота задайте команду вида /train <ссылка на json файл с тренировочными фразами>"
    )


def handle_message(update: Update, context: CallbackContext, project_id):
    text, _ = detect_intent_texts(
        project_id=project_id,
        session_id=update.effective_chat.id,
        text=update.message.text,
        language_code='ru-RU'
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def main() -> None:

    env = Env()
    env.read_env()

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    updater = Updater(token=env('TELEGRAM_TOKEN'), use_context=True)
    project_id = env('DIALOG_FLOW_PROJECT_ID')
    dispatcher = updater.dispatcher

    handle_message_handler = MessageHandler(
        Filters.text & (~Filters.command),
        partial(handle_message, project_id=project_id)
    )
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(handle_message_handler)

    logger.info('Polling started')
    updater.start_polling()


if __name__ == "__main__":
    main()
