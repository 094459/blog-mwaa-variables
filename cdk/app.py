# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

#!/usr/bin/env python3
import io
from aws_cdk import core

from mwaa_cdk.mwaa_cdk_backend import MwaaCdkStackBackend
from mwaa_cdk.mwaa_cdk_env import MwaaCdkStackEnv



# Chnage the mwaa_secret to the identifier you have used
# when creating your secrets via the AWS cli
# The example below is a default value from the blog post that
# supports this script

env_EU=core.Environment(region="eu-central-1", account="704533066374")
mwaa_props = {
    'dagss3location': 'airflow-demo-var',
    'mwaa_env' : 'airflow-demo-var',
    'mwaa_secrets_conn' : 'airflow/connections',
    'mwaa_secrets_var' : 'airflow/variables'
    }

app = core.App()

mwaa_backend = MwaaCdkStackBackend(
    scope=app,
    id="mwaa-network",
    env=env_EU,
    mwaa_props=mwaa_props
)

mwaa_env = MwaaCdkStackEnv(
    scope=app,
    id="mwaa-env",
    vpc=mwaa_backend.vpc,
    env=env_EU,
    mwaa_props=mwaa_props
)



app.synth()
