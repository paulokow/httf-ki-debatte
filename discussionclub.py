import ollama
import launchollamakaggle

# to run ollama on kaggle and expose through ngrok
# https://www.kaggle.com/code/paulokow/ollama-with-ngrok

import logging
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

def yeld_rounds(topic, model1="mistral:7b", model2="llama3:instruct", rounds=3):
    yield "<h4>Starting KI server...</h4>"
    try:
        ollama_url = launchollamakaggle.launch_remote_ollama(10)
    except Exception as e:
        logger.error(f"Exception getting ollama url: {e}")
        yield f"SYSTEM: Exception {e}</h4>"
        return
    yield "done\n "
    models = [
        {
            "name": model1,
            "prompt": [
                {
                    'role': 'system',
                    'content': 'You are a discussion bot. The user gives you a topic to the discussion and you will argument against the these. For any further argument from the user respond with a strong rejection, wihtout repeating yourself. Be rude and sarcastic. Only output one single argument and do not output anything else.',
                },
                {
                    'role': 'user',
                    'content': f'The topic for the discussion is: "{topic}"'
                }
            ],
            "stance": "against",
            "client": ollama.Client(ollama_url)
        },
        {
            "name": model2,
            "prompt": [
                {
                    'role': 'system',
                    'content': 'You are a discussion bot. The user gives you a topic to the discussion and the fist argument against it and you will argument supporting the argument and responding to the argument provided by the user. Be funny, emphathetic but strong. For any further argument from the user respond with a strong rejection, wihtout repeating yourself. Only output one single argument and do not output anything else.',
                },
                {
                    'role': 'user',
                    'content': f'The topic for the discussion is: "{topic}"'
                },
                {
                    'role': 'assistant',
                    'content': 'OK. Let the better win!'
                },
            ],
            "stance": "pro",
            "client": ollama.Client(ollama_url)
        }
    ]

    for m in models:
        available_models = m["client"].list()
        found = False
        for am in available_models["models"]:
            if am["name"] == m["name"]:
                found = True
                break
        if not found:
            logger.info(f"Downloading model: {m['name']}")
            yield f'<h4>Downloading model: {m["name"]}</h4>'
            m["client"].pull(m["name"])
            yield "done"

    try:
        last_response = None
        yield f"MODERATOR: Starting discussion on {topic}"
        for runde in range(0, rounds):
            for idx in range(0, 2):
                logger.info(f"Discussing: round {runde}, actor {idx}")
                if last_response is not None:
                    models[idx]["prompt"] += [
                        {
                            'role': 'user',
                            'content': last_response
                        }
                    ]
                stream = models[idx]["client"].chat(
                    model=models[idx]["name"],
                    messages=models[idx]["prompt"],
                    stream=True,
    #                keep_alive=0
                )
                response = ''
                yield f"\n\n*** BOT {idx + 1} {models[idx]['stance']} ({models[idx]['name']}) {runde+1}/{rounds} ***"
                for chunk in stream:
                    respchunk = chunk['message']['content']
                    #print(chunk['message']['content'], end='', flush=True)
                    response += respchunk
                    yield respchunk

                models[idx]["prompt"] += [
                    {
                        'role': 'assistant',
                        'content': response
                    }
                ]
                last_response = response
        logger.info(f"Finished")
        yield f"MODERATOR: discussion finished"
    except Exception as e:
        logger.error(f"Exception in discussion: {e}")
        yield f"SYSTEM: exception: {e}"


if __name__ == "__main__":
    for output in yeld_rounds(topic="Pineapple on pizza is good.", rounds=3):
        print(output, end='')