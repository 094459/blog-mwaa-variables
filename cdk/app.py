# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

#!/usr/bin/env python3
import io
from aws_cdk import core

from mwaa_cdk.mwaa_cdk_backend import MwaaCdkStackBackend
from mwaa_cdk.mwaa_cdk_env import MwaaCdkStackEnv
from mwaa_cdk.mwaa_bastion import MwaaCdkStackBastion
from mwaa_cdk.mwaa_cdk_cicd import MwaaCdkStackCICD


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

# To do - not currently implemented so check back
# later 

mwaa_cicd = MwaaCdkStackCICD(
    scope=app,
    id="mwaa-cicd",
    env=env_EU,
    vpc=mwaa_backend.vpc,
    mwaa_props=mwaa_props
)
# If you want to configure a Private MWAA environment
# You can deploy the bastion stack which will give you 
# an endpoint on which to create your ssh-tunnel

mwaa_bastion = MwaaCdkStackBastion(
    scope=app,
    id="mwaa-bastion",
    vpc=mwaa_backend.vpc,
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
