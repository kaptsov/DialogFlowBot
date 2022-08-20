import json
from argparse import ArgumentParser

from environs import Env
from google.cloud.dialogflow import (
    SessionsClient, TextInput, QueryInput,
    IntentsClient, AgentsClient, Intent, ListIntentsRequest
)


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = TextInput(text=text, language_code=language_code)
    query_input = QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return (
        response.query_result.fulfillment_text,
        response.query_result.intent.is_fallback
    )


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = IntentsClient()

    parent = AgentsClient.agent_path(project_id)

    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = Intent.Message.Text(text=[message_texts])
    message = Intent.Message(text=text)

    intent = Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )

    intents_client.create_intent(
        request={'parent': parent, 'intent': intent}
    )


def get_intents(project_id):
    client = IntentsClient()
    parent = AgentsClient.agent_path(project_id)

    request = ListIntentsRequest(
        parent=parent,
        language_code='ru',
    )
    list_intents = [response.display_name for response in client.list_intents(request=request)]

    return list_intents


def main():
    env = Env()
    env.read_env()

    parser = ArgumentParser()
    parser.add_argument('path_to_json', help='Полный путь к json файлу')
    args = parser.parse_args()

    project_id = env('DIALOG_FLOW_PROJECT_ID')

    with open(args.path_to_json, 'r', encoding='utf-8') as intents_file:
        intents_to_add = json.load(intents_file)

    print('Загружаем фразы в DialogFlow...')
    intents_collection = get_intents(project_id)

    for display_name, content in intents_to_add.items():
        if display_name not in intents_collection:
            print(f'Добавляем обработку "{display_name}"')
            create_intent(
                project_id=project_id,
                display_name=display_name,
                training_phrases_parts=content['questions'],
                message_texts=content['answer'],
            )

        else:
            print(f'Обработка "{display_name}" уже существует')
    print('Загружено')


if __name__ == '__main__':
    main()