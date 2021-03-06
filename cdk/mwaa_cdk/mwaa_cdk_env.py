# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_deployment as s3deploy
import aws_cdk.aws_mwaa as mwaa
import aws_cdk.aws_iam as iam
import aws_cdk.aws_secretsmanager as secretsmanager
import aws_cdk.aws_kms as kms


class MwaaCdkStackEnv(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, mwaa_props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
       
        # Create MWAA S3 Bucket and upload local dags 

        dags_bucket = s3.Bucket(
            self,
            "mwaa-dags",
            bucket_name=f"{mwaa_props['dagss3location'].lower()}",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        s3deploy.BucketDeployment(self, "DeployDAG",
        sources=[s3deploy.Source.asset("./dags")],
        destination_bucket=dags_bucket,
        destination_key_prefix="dags",
        prune=False,
        retain_on_delete=False
        )
        
        dags_bucket_arn = dags_bucket.bucket_arn

        # define your own KMS key to encrypt everything
        # can disable this, make sure you alter the IAM policy if you do that
        # change the line  f"arn:aws:kms:{self.region}:{self.account}:key/{key.key_id}" to "*"

        key = kms.Key(self, f"{mwaa_props['mwaa_env']}Key", enable_key_rotation=True)
        key.add_alias(f"alias/{mwaa_props['mwaa_env']}")    

        # Create MWAA IAM Policies and Roles, copied from MWAA documentation site

        mwaa_policy_document = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    actions=["airflow:PublishMetrics"],
                    effect=iam.Effect.ALLOW,
                    resources=[f"arn:aws:airflow:{self.region}:{self.account}:environment/{mwaa_props['mwaa_env']}"],
                ),
                iam.PolicyStatement(
                    actions=[
                        "s3:ListAllMyBuckets"
                    ],
                    effect=iam.Effect.DENY,
                    resources=[
                        f"{dags_bucket_arn}/*",
                        f"{dags_bucket_arn}"
                        ],
                ),
                iam.PolicyStatement(
                    actions=[
                        "s3:GetObject*",
                        "s3:GetBucket*",
                        "s3:List*"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[
                        f"{dags_bucket_arn}/*",
                        f"{dags_bucket_arn}"
                        ],
                ),
                iam.PolicyStatement(
                    actions=[
                        "logs:CreateLogStream",
                        "logs:CreateLogGroup",
                        "logs:PutLogEvents",
                        "logs:GetLogEvents",
                        "logs:GetLogRecord",
                        "logs:GetLogGroupFields",
                        "logs:GetQueryResults"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[f"arn:aws:logs:{self.region}:{self.account}:log-group:airflow-{mwaa_props['mwaa_env']}-*"],
                ),
                iam.PolicyStatement(
                    actions=[
                        "logs:DescribeLogGroups"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    actions=[
                        "sqs:ChangeMessageVisibility",
                        "sqs:DeleteMessage",
                        "sqs:GetQueueAttributes",
                        "sqs:GetQueueUrl",
                        "sqs:ReceiveMessage",
                        "sqs:SendMessage"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[f"arn:aws:sqs:{self.region}:*:airflow-celery-*"],
                ),
                iam.PolicyStatement(
                    actions=[
                        "kms:Decrypt*",
                        "kms:Describe*",
                        "kms:ReEncrypt*",
                        "kms:GenerateDataKey*",
                        "kms:Encrypt*"
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[
                        f"arn:aws:kms:{self.region}:{self.account}:key/{key.key_id}"
                        ],                 
                    conditions={
                        "StringEquals": {
                            "kms:ViaService": [
                                f"sqs.{self.region}.amazonaws.com",
                                f"s3.{self.region}.amazonaws.com",
                            ]
                        }
                    },
                ),
            ]
        )

        mwaa_service_role = iam.Role(
            self,
            "mwaa-service-role",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("airflow.amazonaws.com"),
                iam.ServicePrincipal("airflow-env.amazonaws.com"),
            ),
            inline_policies={"CDKmwaaPolicyDocument": mwaa_policy_document},
            path="/service-role/"
        )

        # Create MWAA Security Group and get networking info

        security_group = ec2.SecurityGroup(
            self,
            id = "mwaa-sg",
            vpc = vpc,
            security_group_name = "mwaa-sg"
        )

        security_group_id = security_group.security_group_id
        
        security_group.connections.allow_internally(ec2.Port.all_traffic(),"MWAA")

        subnets = [subnet.subnet_id for subnet in vpc.private_subnets]
        network_configuration = mwaa.CfnEnvironment.NetworkConfigurationProperty(
            security_group_ids=[security_group_id],
            subnet_ids=subnets,
        )

        # Configure specific MWAA settings - you can externalise these if you want

        logging_configuration = mwaa.CfnEnvironment.LoggingConfigurationProperty(
            task_logs=mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(enabled=True, log_level="INFO"),
            worker_logs=mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(enabled=True, log_level="INFO"),
            scheduler_logs=mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(enabled=True, log_level="INFO"),
            dag_processing_logs=mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(enabled=True, log_level="INFO"),
            webserver_logs=mwaa.CfnEnvironment.ModuleLoggingConfigurationProperty(enabled=True, log_level="INFO")
            )

        # these are custom MWAA / Apache Airflow configurations
        # these currently enable AWS Secrets manager for lookups for variables
        # as defined in the app.py props file. They are MWAA version specific

        ## MWAA version 1.x

        #options = {
        #    'core.load_default_connections': False,
        #    'core.load_examples': False,
        #    'webserver.dag_default_view': 'tree',
        #    'secrets.backend' : 'airflow.contrib.secrets.aws_secrets_manager.SecretsManagerBackend',
        #    ''secrets.backend_kwargs' : { "connections_prefix" : f"{mwaa_props['mwaa_secrets_conn']}" , "variables_prefix" : f"{mwaa_props['mwaa_secrets_var']}" },
        #    'webserver.dag_orientation': 'TB'
        #    }
        
        ## MWAA version 2.x

        options = {
            'core.load_default_connections': False,
            'core.load_examples': False,
            'webserver.dag_default_view': 'tree',
            'secrets.backend' : 'airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend',
            'secrets.backend_kwargs' : { "connections_prefix" : f"{mwaa_props['mwaa_secrets_conn']}" , "variables_prefix" : f"{mwaa_props['mwaa_secrets_var']}" } ,
            'webserver.dag_orientation': 'TB'
        }


        # You need to provide access to AWS Secrets that can be used by MWAA and grant access
        # to MWAA execution role. Use this if you want to define variables for your environment
        # First create the secrets and then grab the secrets ARN which you can put in here

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
                            resources=[
                                f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:{mwaa_props['mwaa_secrets_var']}*",
                                f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:{mwaa_props['mwaa_secrets_conn']}*",
                                ],
                        ),
                    ]
        )
        mwaa_service_role.attach_inline_policy(mwaa_secrets_policy_document)

        tags = {
            'env': f"{mwaa_props['mwaa_env']}",
            'service': 'MWAA Apache AirFlow'
        }
        

        
        # Create MWAA environment using all the info above

        managed_airflow = mwaa.CfnEnvironment(
            scope=self,
            id='airflow-blog-environment',
            name=f"{mwaa_props['mwaa_env']}",
            airflow_configuration_options={'core.default_timezone': 'utc'},
            #airflow_version='1.10.12',
            airflow_version='2.0.2',
            dag_s3_path="dags",
            environment_class='mw1.small',
            execution_role_arn=mwaa_service_role.role_arn,
            kms_key=key.key_id,
            logging_configuration=logging_configuration,
            max_workers=5,
            network_configuration=network_configuration,
            #plugins_s3_object_version=None,
            #plugins_s3_path=None,
            #requirements_s3_object_version=None,
            #requirements_s3_path=None,
            source_bucket_arn=dags_bucket_arn,
            webserver_access_mode='PUBLIC_ONLY',
            #weekly_maintenance_window_start=None
        )

        managed_airflow.add_override('Properties.AirflowConfigurationOptions', options)
        managed_airflow.add_override('Properties.Tags', tags)

        core.CfnOutput(
            self,
            id="MWAAURL",
            value=managed_airflow.attr_webserver_url,
            description="DNS of the MWAA WebServer"
        )
        core.CfnOutput(
            self,
            id="MWAADAG",
            value=managed_airflow.dag_s3_path,
            description="MWAA DAG location on S3"
        )
        core.CfnOutput(
            self,
            id="MWAAEXE",
            value=managed_airflow.execution_role_arn,
            description="MWAA Execution role"
        )
    



