import ollama
import datetime
from jinja2 import Environment, FileSystemLoader
import ngrok
import json
from time import sleep
import os

from dotenv import load_dotenv
load_dotenv()

def get_running_session_url(wait=False):
    # Construct the NGROK API client
    client = ngrok.Client(os.getenv("NGROK_API_KEY"))

    while True:
        # List all online tunnels
        for t in client.tunnels.list():
            if t.metadata is not None:
                try:
                    metadata_json = json.loads(t.metadata)
                    if 'name' in metadata_json and metadata_json['name'] == "ollama_tunnel":
                        print(f"Tunnel found: {t.public_url} {metadata_json['start']} {metadata_json['end']}")
                        return t.public_url
                except json.JSONDecodeError:
                    pass
            print(t)
        if not wait:
            break
        sleep(10)
    return None

def launch_remote_ollama(tunnel_run_time_minutes=60):
    # import kaggle later after env is initiated (otherwise error of not existing config file   )
    from kaggle import KaggleApi
    from kaggle.models import KernelPushRequest

    url = get_running_session_url()
    if url is not None:
        print(f"Session running: {url}")
        return url
    # preprocess kaggle notebook with jinja2
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notebook_templates')))
    template = env.get_template('ollama-with-ngrok.ipynb')
    start_time = datetime.datetime.utcnow()
    end_time = start_time + datetime.timedelta(minutes=tunnel_run_time_minutes)
    tunnel_metadata = json.dumps({
        "name": "ollama_tunnel",
        "start": start_time.isoformat(),
        "end": end_time.isoformat()
    }).replace("\"", "\\\"")
    #tunnel_metadata = f"ollama_tunnel_{end_time.isoformat()}"
    output_from_parsed_template = template.render(tunnel_run_time_minutes=tunnel_run_time_minutes, tunnel_metadata=tunnel_metadata)
    #with open("temp.ipynb", "w") as f:
    #    f.write(output_from_parsed_template)
    kaggle_request = KernelPushRequest(
        slug='paulokow/ollama-with-ngrok-lite2',
        new_title='ollama-with-ngrok-lite2',
        text = output_from_parsed_template,
        enable_gpu=True,
        is_private=True,
        dataset_data_sources=[],
        kernel_data_sources=[],
        language='python',
        kernel_type='notebook',
        enable_internet=True
    )
    
    api = KaggleApi()
    api.authenticate()
    list = api.kernels_list(mine=True)
    result = api.kernel_push(kaggle_request)
    print(result)

    url = get_running_session_url(True)
    print(f"Session running: {url}")
    return url

if __name__ == "__main__":
    launch_remote_ollama(10)
