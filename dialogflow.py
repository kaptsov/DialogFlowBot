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
    list_intents = []
    for response in client.list_intents(request=request):
        list_intents.append(response.display_name)
    return list_intents
