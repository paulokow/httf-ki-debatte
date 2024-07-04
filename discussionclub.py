import ollama

# to run ollama on kaggle and expose through ngrok
# https://www.kaggle.com/code/paulokow/ollama-with-ngrok



def yeld_rounds(topic, model1="mistral:7b", model2="llama3:instruct", rounds=3):
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
            "client": ollama.Client("https://bd54-35-247-42-227.ngrok-free.app")
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
            "client": ollama.Client("https://bd54-35-247-42-227.ngrok-free.app")
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
            yield f'Downloading model: {m["name"]}'
            m["client"].pull(m["name"])

    last_response = None
    yield f"Starting discussion on {topic}"
    for runde in range(0, rounds):
        for idx in range(0, 2):
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


if __name__ == "__main__":
    for output in yeld_rounds(topic="Pineapple on pizza is good.", rounds=3):
        print(output, end='')