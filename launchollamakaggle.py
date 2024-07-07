import ollama
import datetime
from jinja2 import Environment, FileSystemLoader
import ngrok
import json
from time import sleep
import os


import logging
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

from dotenv import load_dotenv
load_dotenv()

def get_running_session_url(wait=False, max_tries=10):
    # Construct the NGROK API client
    client = ngrok.Client(os.getenv("NGROK_API_KEY"))
    for counter in range(max_tries):
        logger.info(f"Trying to get running session url {counter}")
        # List all online tunnels
        for t in client.tunnels.list():
            if t.metadata is not None:
                try:
                    metadata_json = json.loads(t.metadata)
                    if 'name' in metadata_json and metadata_json['name'] == "ollama_tunnel":
                        logger.info(f"Tunnel found: {t.public_url} {metadata_json['start']} {metadata_json['end']}")
                        return t.public_url
                except json.JSONDecodeError:
                    pass
            logger.info(f"{t}")
        if not wait:
            break
        sleep(10)
    return None

def start_kaggle_notebook(ngrok_metadata, tunnel_run_time_minutes):
    from kaggle.api.kaggle_api_extended import KaggleApi
    from kaggle.models import KernelPushRequest
    # preprocess kaggle notebook with jinja2
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notebook_templates')))
    template = env.get_template('ollama-with-ngrok.ipynb')
    output_from_parsed_template = template.render(tunnel_run_time_minutes=tunnel_run_time_minutes, tunnel_metadata=ngrok_metadata)
    kaggle_request = KernelPushRequest(
        slug=f'{os.getenv("KAGGLE_USERNAME")}/ollama-with-ngrok-lite2',
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
    result = api.kernel_push(kaggle_request)
    logger.info(f"Kaggle result: {result}")


def launch_remote_ollama(tunnel_run_time_minutes=60):
    if os.getenv("KAGGLE_USERNAME") is None or os.getenv("KAGGLE_KEY") is None or os.getenv("NGROK_API_KEY") is None:
        # try local ollama
        logger.warn(f"Configuration missing. Trying local ollama")
        try:
            logger.info(f"Available models: \n{ollama.list()}")
            return "http://localhost:11434"
        except:
            logger.error(f"No local ollama running and Kaggle username or key or ngrok api key not set. Use KAGGLE_USERNAME, KAGGLE_KEY and NGROK_API_KEY environment variables or start ollama locally.")
            raise ConnectionError(f"No local ollama running and Kaggle username or key or ngrok api key not set. Use KAGGLE_USERNAME, KAGGLE_KEY and NGROK_API_KEY environment variables or start ollama locally.")

    url = get_running_session_url()
    if url is not None:
        logger.info(f"Session running: {url}")
        return url
    start_time = datetime.datetime.utcnow()
    end_time = start_time + datetime.timedelta(minutes=tunnel_run_time_minutes)
    tunnel_metadata = json.dumps({
        "name": "ollama_tunnel",
        "start": start_time.isoformat(),
        "end": end_time.isoformat()
    }).replace("\"", "\\\"")
    start_kaggle_notebook(tunnel_metadata, tunnel_run_time_minutes)

    url = get_running_session_url(True)
    logger.info(f"Session running: {url}")
    return url

if __name__ == "__main__":
    launch_remote_ollama(10)
