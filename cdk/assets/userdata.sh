#!/bin/bash -e
#
# Set tcp forwarding to true which is rquired for MWAA/Proxy forwarding
# https://docs.aws.amazon.com/mwaa/latest/userguide/tutorials-private-network-bastion.html
# 
# To do get the bastion_bootstrap.sh from a better location

curl -O https://aws-quickstart-us-east-1.s3.us-east-1.amazonaws.com/quickstart-linux-bastion/scripts/bastion_bootstrap.sh
chmod +x bastion_bootstrap.sh
sudo ./bastion_bootstrap.sh --tcp-forwarding true