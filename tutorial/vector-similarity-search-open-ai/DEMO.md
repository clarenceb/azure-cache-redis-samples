# Demo Steps

## Setup Python Virtual Environment

```sh
python -V
# Python 3.12.3

python -mvenv .venv

source .venv/bin/activate
pip install -r requirements.txt
```

## Install VSCode extensions

* Python (Microsoft)
* Python Environments (Microsoft)
* Jupyter (Microsoft)

## Create Azure Resources

### Azure Managed Redis

* Balanced: vCPUS 4, Cache 12GB, SKU B10
* Public endpoint
* Cluster Policy: Enterprise
* Modules: RediSearch
* Access Key Authentication: enable

### Azure OpenAI Service

* Type: All networks
* Create the resource
* Open [Aure AI Foundry Deployments](https://ai.azure.com/resource/deployments)
* Create the following deployments:
    * Model 1: text-embedding-3-large / Global Standard / 250K TPM
    * Model 2: gpt-4o-mini / Global Standard / 250K TPM

## Create a `.env` file with these values

```sh
API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
RESOURCE_ENDPOINT=https://xxxxxxxxxxxxxxx.openai.azure.com
DEPLOYMENT_NAME=text-embedding-3-large
MODEL_NAME=text-embedding-3-large
REDIS_ENDPOINT=xxxxxxxxxxx.<region>.redis.azure.net:10000
REDIS_PASSWORD=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Open Jupyter notebook

Select the `.venv/bin/python` virtual environment for the Kernel.

Execute each of the cells.

## Run then movie chat

```sh
python movie-chat.py

# What movies has Tom Cruise been in?
# What actor did I just ask about?
# What years has he been in movies?
# Just display the years as a comma-separate list and nothig else
# Tell me about Top Gun
# q
```
