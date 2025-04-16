#!/bin/bash

openAIServiceEndpoint=$(az deployment group show -g movie-chat-amr -n movie-chat-amr --query "properties.outputs.openAIServiceEndpoint.value" -o tsv)
openAIApiKey=$(az cognitiveservices account keys list --name aoai-3o4hqx57thpu6 --resource-group movie-chat-amr --query key1 -o tsv)
redisCacheEndpoint=$(az deployment group show -g movie-chat-amr -n movie-chat-amr --query "properties.outputs.redisCacheEndpoint.value" -o tsv)
redisCacheName=$(az deployment group show -g movie-chat-amr -n movie-chat-amr --query "properties.outputs.redisCacheName.value" -o tsv)
redisPassword="manually-set-password"

echo "OpenAI Service Endpoint: $openAIServiceEndpoint"
echo "Redis Cache Endpoint: $redisCacheEndpoint"
echo "Redis Cache Name: $redisCacheName"

cat <<EOF > .env
API_KEY=$openAIApiKey
RESOURCE_ENDPOINT=$openAIServiceEndpoint
DEPLOYMENT_NAME=text-embedding-3-large
MODEL_NAME=text-embedding-3-large
REDIS_ENDPOINT=$redisCacheEndpoint:10000
REDIS_PASSWORD=$redisPassword
EOF
