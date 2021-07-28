from aws_cdk import core
import aws_cdk.aws_ec2 as ec2

class MwaaCdkStackCICD(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, mwaa_props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
   
        # Create Pipeline to automatically deploy your DAGs









