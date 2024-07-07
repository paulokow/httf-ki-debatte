# AI Discussion club

The goal of this project is to let different AI models discuss with each other on different topics provided by the user.
This project was inspired by the projects created by participants of [Hack To The Future](https://hacktothefuture.de) hackathon in June'24.

## Prerequisites

This project can be run with local ollama instance or it can create and access remote ollama instance with Kaggle and ngrok.

For Kaggle it is important, that the account is fully verified, with both e-mail and telephone number so that it has access to 30h of GPU resources per week.
To check is please go in the [Kaggle Setting Panel](https://www.kaggle.com/settings).

## Configuration Guide: Environment Variables

To run this project, you'll need to set up some environment variables. Here's a step-by-step guide on how to do it.
These configuration variables are not needed if local ollama instance is used.

### 1. Create a `.env` file

Create a new file called `.env` in the root directory of your project. This file will contain all your environment variable settings.

Environment variables can be also provided directly, as supported by the deployment platform.

### 2. Set the environment variables

In the `.env` file, add the following lines:
```properties
NGROK_API_KEY=YOUR_API_KEY_HERE
KAGGLE_USERNAME=YOUR_KAGGLE_USERNAME_HERE
KAGGLE_KEY=YOUR_KAGGLE_KEY_HERE
```

Replace `YOUR_API_KEY_HERE`, `YOUR_KAGGLE_USERNAME_HERE`, and `YOUR_KAGGLE_KEY_HERE` with your actual values.

Description of environment variables:
- `NGROK_API_KEY`: Your Ngrok API key, used to tunnel ollama instance to the internet. The key can be obtained in [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken).
- `KAGGLE_USERNAME`: Your Kaggle username.
- `KAGGLE_KEY`: Your Kaggle API key.
Unless you already have `kaggle.json` (usually located in the home folder under `.kaggle`) you can obtain it in the [Kaggle Setting Panel](https://www.kaggle.com/settings) using `Create New Token`. The JSON file that you get contains both the username and the key.

## Installation

### (OPTIONAL) create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### install requirements

```bash
pip install -r requirements.txt
```

## Running

### Start server in develompent mode

```bash
export FLASK_APP=app.py
flask run --host 0.0.0.0 --port 5000
```

### Start the first discussion

If you use local ollama there is nothing else to do.

For remote ollama, after the first run (which will fail to start ngrok) you need to find the newly created notebook named `ollama-with-ngrok-lite2` in your account and assign a secret `NGROK` with ngrok key to it, so that the notebook can access ngrok. See [this tutorial](https://www.kaggle.com/discussions/general/414523) for the description of the process.
A direct link to the notebook will also appear in the server logs:
```
INFO in launchollamakaggle: Kaggle result: {... 'url': 'https://www.kaggle.com/code/exampleuser/ollama-with-ngrok-lite2', ...}
```