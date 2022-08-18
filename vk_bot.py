import random

import vk_api as vk
from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType

from dialogflow_func import detect_intent_texts

env = Env()
env.read_env()

def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000)
    )


def on_message(event, vk_api):
    message, is_fallback = detect_intent_texts(
        project_id=env('DIALOG_FLOW_PROJECT_ID'),
        session_id=event.user_id,
        text=event.text,
        language_code='ru-RU'
    )

    if is_fallback:
        vk_api.messages.markAsRead(peer_id=event.user_id)
        return

    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        random_id=random.randint(1, 1000)
    )


def main():

    vk_session = vk.VkApi(token=env('VK_KEY'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            on_message(event, vk_api)


if __name__ == "__main__":
    main()
