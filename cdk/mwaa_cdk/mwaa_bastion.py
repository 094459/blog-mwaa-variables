from aws_cdk import core
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_mwaa as mwaa
import aws_cdk.aws_iam as iam

ec2_type = "t3.micro"

with open("assets/userdata.sh") as f:
    user_data = f.read()

class MwaaCdkStackBastion(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, mwaa_props,  **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
       
        # Create Bastion Host security group

        bastion_sg = ec2.SecurityGroup(
            self,
            id="bastion-sg",
            security_group_name='mwaa-bastion-sg',
            description='Enable ssh access to restricted clients only',
            vpc=vpc,
            allow_all_outbound=True
        )

        # Create the Bastion Host

        bastion = ec2.BastionHostLinux(
            self,
            id="BastionHost",
            vpc=vpc,
            instance_name="BastionHost",
            security_group=bastion_sg,
            instance_type=ec2.InstanceType(ec2_type),
            subnet_selection=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            )
        )

        ## Setup key_name for EC2 instance login if you don't use Session Manager
        ## Create keypair in AWS console


        key_name = "frank-open-distro"
        bastion.instance.instance.add_property_override("KeyName", key_name)

        ## Change .any_ipv4 to a specific IP address/range to reduce attack surface
        
        bastion.allow_ssh_access_from(ec2.Peer.any_ipv4())
        #bastion.allow_ssh_access_from(ec2.Peer.ipv4('10.44.0.0/24'))
        ec2.CfnEIP(self, id="BastionHostEIP", domain="vpc", instance_id=bastion.instance_id)

        core.CfnOutput(
            self,
            id="BastionPrivateIP",
            value=bastion.instance_private_ip,
            description="BASTION Private IP",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:bastion-private-ip"
        )

        core.CfnOutput(
            self,
            id="BastionPublicIP",
            value=bastion.instance_public_ip,
            description="BASTION Public IP",
            export_name=f"{self.region}:{self.account}:{self.stack_name}:bastion-public-ip"
        )


    



