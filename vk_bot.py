import random

import vk_api as vk
from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType

from dialogflow import detect_intent_texts


def handle_message(event, vk_api, project_id):

    message, is_fallback = detect_intent_texts(
        project_id=project_id,
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

    env = Env()
    env.read_env()

    vk_session = vk.VkApi(token=env('VK_KEY'))
    project_id = env('DIALOG_FLOW_PROJECT_ID')
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_message(event, vk_api, project_id)


if __name__ == "__main__":
    main()
