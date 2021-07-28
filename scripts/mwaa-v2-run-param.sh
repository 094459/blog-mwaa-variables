# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

#!/bin/bash


[ $# -eq 0 ] && echo "Usage: $0 MWAA environment name, name of the DAG and runtime parameters " && exit

if [[ $2 == "" ]]; then
    dag="dags list"

elif [ $2 == "trigger_dag" ] && [[ $3 != "" ]]; then
    dag="dags trigger $3 $4 $5"
    
elif [ $2 == "list_dags" ] || [ $2 == "version" ]; then
    dag=$2

elif [ $2 == "variables" ] ; then
    dag="$2 $3 $4 $5"

else
    echo "Not a valid command"
    exit 1
fi

echo $dag


CLI_JSON=$(aws mwaa --region $AWS_REGION create-cli-token --name $1) \
    && CLI_TOKEN=$(echo $CLI_JSON | jq -r '.CliToken') \
    && WEB_SERVER_HOSTNAME=$(echo $CLI_JSON | jq -r '.WebServerHostname') \
    && CLI_RESULTS=$(curl --request POST "https://$WEB_SERVER_HOSTNAME/aws_mwaa/cli" \
    --header "Authorization: Bearer $CLI_TOKEN" \
    --header "Content-Type: text/plain" \
    --data-raw "$dag" ) \
    && echo "Output:" \
    && echo $CLI_RESULTS | jq -r '.stdout' | base64 --decode \
    && echo "Errors:" \
    && echo $CLI_RESULTS | jq -r '.stderr' | base64 --decode
