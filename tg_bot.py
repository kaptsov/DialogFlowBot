import logging
import os

import requests
from telegram import Update, ForceReply
from telegram.ext import \
    Updater,\
    CallbackContext,\
    CommandHandler,\
    MessageHandler,\
    Filters

from .dialogflow_func import \
    get_list_intents,\
    create_intent,\
    detect_intent_texts

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
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


def on_message(update: Update, context: CallbackContext):
    text = detect_intent_texts(
        project_id=os.environ['DIALOG_FLOW_PROJECT_ID'],
        session_id=update.effective_chat.id,
        text=update.message.text,
        language_code='ru-RU'
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command."
    )


def df_train(update: Update, context: CallbackContext):
    if not context.args:
        help(update, context)
        return
    try:
        response = requests.get(context.args[0])
        response.raise_for_status()
    except requests.exceptions.MissingSchema:
        help(update, context)
        return

    project_id = os.environ['DIALOG_FLOW_PROJECT_ID']

    intents_to_add = response.json()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Загружаем фразы в DialogFlow...')
    list_intents = get_list_intents(project_id)

    for display_name, content in intents_to_add.items():
        if display_name not in list_intents:
            context.bot.send_message(chat_id=update.effective_chat.id,
                text=f'Добавляем обработку "{display_name}"'
            )
            create_intent(
                project_id=project_id,
                display_name=display_name,
                training_phrases_parts=content['questions'],
                message_texts=content['answer'],
            )

        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                text=f'Обработка "{display_name}" уже существует'
            )
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Загружено')


def main() -> None:
    updater = Updater(token=os.environ['TELEGRAM_TOKEN'], use_context=True)
    dispatcher = updater.dispatcher

    on_message_handler = MessageHandler(
        Filters.text & (~Filters.command), on_message
    )
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)
    df_train_handler = CommandHandler('train', df_train)
    unknown_handler = MessageHandler(Filters.command, unknown)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(df_train_handler)
    dispatcher.add_handler(on_message_handler)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
