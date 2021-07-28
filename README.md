### How to use this repository

These scripts and DAGs are used in the blog post Working with parameters and variables in your Amazon Managed Workflows for Apache Airflow environment.

**MWAA CDK**

This repository also contains a CDK app that will provision a MWAA environment that you can use as part of this blog post walk through. To set this up, you will need to have access to an AWS Account, CDK and an AWS region that supports MWAA.

To deplpy MWAA, all you need to do is:

1. Update the app.py , changing the values below which should be unique for your environment. For the dagss3location, this is a unique S3 bucket that will get created, so ensure this is available and unique. If not the CDK app will fail

```
env_EU=core.Environment(region="{aws reguib}", account="{your aws account}")
mwaa_props = {
    'dagss3location': 'airflow-demo-var',
    'mwaa_env' : 'airflow-demo-var',
    'mwaa_secrets_conn' : 'airflow/connections',
    'mwaa_secrets_var' : 'airflow/variables'
```

2. Once updated and saved, you can deploy with the following commands

```
cdk deploy mwaa-network
cdk deploy mwaa-env
```

You will be prompted to confirm some IAM roles that will get provisioned. Answer Y if you want to proceed, and after around 20-25 minutes, the build should complete.

3. To delete this environment, you need to run the following 

```
cdk destroy mwaa-env
cdk destroy mwaa-network
```
You then need to delete the S3 bucket that was created.

4. Depending on what else you configured following along from the blog post, make sure you review/remove

* any secrets you defined in the AWS Secrets Manager

### Enabling AWS Secrets Manager in MWAA

The following is how we enable the AWS Secrets Manager integration with MWAA, which you can see in the CDK code

```
         options = {
            'core.load_default_connections': False,
            'core.load_examples': False,
            'webserver.dag_default_view': 'tree',
            # MWAA v1.x 'secrets.backend' : 'airflow.contrib.secrets.aws_secrets_manager.SecretsManagerBackend',
            'secrets.backend' : 'airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend',
            'secrets.backend_kwargs' : { "connections_prefix" : f"{mwaa_props['mwaa_secrets_conn']}" , "variables_prefix" : f"{mwaa_props['mwaa_secrets_var']}" ,
            'webserver.dag_orientation': 'TB'
            }

        mwaa_secrets_policy_document = iam.Policy(self, "MWAASecrets", 
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "secretsmanager:GetResourcePolicy",
                                "secretsmanager:GetSecretValue",
                                "secretsmanager:DescribeSecret",
                                "secretsmanager:ListSecretVersionIds",
                                "secretsmanager:ListSecrets"
                            ],
                            effect=iam.Effect.ALLOW,
                            resources=[f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:{mwaa_props['mwaa_secrets']}*"],
                        ),
                    ]
        )
        mwaa_service_role.attach_inline_policy(mwaa_secrets_policy_document)

```

Once you save you can then redeploy.  
