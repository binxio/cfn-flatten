from resolve import TemplateParser

def construct_arn(resource_name, service, resource=None, slash_resource=False, global_service=False, no_account=False, ctx: TemplateParser=None):
    region = ctx.region
    account = ctx.account
    partition = "aws" # TODO
    return f"arn:{partition}:{service}:{region if not global_service else ''}:{account if not no_account else ''}{':'+resource if resource else ''}{':' if not slash_resource else '/'}{resource_name}"

def safe_get(id, obj, k, att=None, ctx: TemplateParser=None):
    value = None
    if 'Properties' in obj['json']:
        if k in obj['json']['Properties']:
            ctx.json_extract(obj['json']['Properties'][k], obj['json']['Properties'], k)
        value = obj['json']['Properties'].get(k, None)
    if not value and att:
        if 'Metadata' not in obj['json']:
            obj['json']['Metadata'] = {}
        key = "aws:resolver:" + k
        if key in obj['json']['Metadata']:
            value = obj['json']['Metadata'][key]
        else:
            value = id.lower()
            obj['json']['Metadata'][key] = value
    return value

class Generic:
    @staticmethod
    def get_attribute(name):
        def internal_get_attribute(id, o, att, ctx):
            rid = safe_get(id, o, name, 'Ref', ctx)
            if att == 'Ref':
                return rid
            if att == 'GroupId':
                return rid
            raise Exception(f"Unknown attribute Generic {id} {att}")

        return internal_get_attribute

class GenericWithArn:
    @staticmethod
    def get_attribute(name, service, resource, slash_resource=False, global_service=False, ref_is_arn=False, append_to_id=""):
        def internal_get_attribute(id, o, att, ctx):
            rid = safe_get(id+append_to_id, o, name, 'Ref', ctx)
            if att == 'Ref':
                if not ref_is_arn:
                    return rid
            if att == 'Arn' or (att == 'Ref' and ref_is_arn):
                return construct_arn(rid, service, resource, slash_resource, global_service, ctx=ctx)
            raise Exception(f"Unknown attribute Generic {id} {att}")

        return internal_get_attribute

class Role:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        # to do which att
        name = safe_get(id, o, 'RoleName', 'Ref', ctx)
        path = safe_get(id, o, 'Path', ctx=ctx)
        if att == 'Ref':
            return name
        parts = [name]
        if path:
            parts.insert(0, path)
        name_and_path = "/".join(parts)
        if att == 'Arn':
            return construct_arn(name_and_path, service="iam", resource="role", slash_resource=True, global_service=True, ctx=ctx)
        raise Exception(f"Unknown attribute AWS::IAM::Role {id} {att}")

class Function:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        name = safe_get(id, o, 'FunctionName', 'Ref', ctx)
        if att == 'Ref':
            return name
        if att == 'Arn':    
            return construct_arn(name, service="lambda", resource="function", ctx=ctx)
        raise Exception(f"Unknown attribute AWS::Lambda::Function {id} {att}")

class Parameter:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        param_name = safe_get(id, o, 'Name', 'Ref', ctx)
        if att == 'Ref':
            return param_name
        if att == 'Arn':
            return construct_arn(param_name, service="ssm", resource="parameter", ctx=ctx)
        if att == 'Value':
            return o['json']['Properties']['Value']
        raise Exception(f"Unknown attribute AWS::S3::Bucket {id} {att}")

class Bucket:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        bucket_name = safe_get(id, o, 'BucketName', 'Ref', ctx)
        if att == 'Ref':
            return bucket_name
        if att == 'RegionalDomainName':
            return f'{bucket_name}.s3.{ctx.refs["AWS::Region"]}.amazonaws.com'
        if att == 'Arn':
            return construct_arn(bucket_name, service="s3", no_account=True, global_service=True, ctx=ctx)
        raise Exception(f"Unknown attribute AWS::S3::Bucket {id} {att}")

class Key:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        key_id = safe_get(id, o, 'KeyId', 'Ref', ctx)
        if att == 'Ref':
            return key_id
        if att == 'Arn':
            return construct_arn(key_id, service="kms", resource="key", slash_resource=True, ctx=ctx)
        raise Exception(f"Unknown attribute AWS::KMS::Key {id} {att}")

class InstanceProfile:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        rid = safe_get(id, o, 'InstanceProfileName', 'Ref', ctx)
        if att == 'Ref':
            return rid
        if att == 'Arn':
            return construct_arn(rid, service="iam", resource="instance-profile", slash_resource=True, ctx=ctx),
        raise Exception(f"Unknown attribute AWS::IAM::InstanceProfile {id} {att}")

class Application:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        rid = safe_get(id, o, 'ApplicationName', 'Ref', ctx)
        if att == 'Ref':
            return rid
        raise Exception(f"Unknown attribute AWS::CodeDeploy::Application {id} {att}")

class Repository:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        rid = safe_get(id, o, 'RepositoryName', 'Ref', ctx)
        if att == 'Ref':
            return rid
        if att == 'Name':
            return rid
        if att == 'Arn':
            return construct_arn(rid, service="codecommit", ctx=ctx)
        raise Exception(f"Unknown attribute AWS::CodeCommit::Repository {id} {att}")

class Project:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        rid = safe_get(id, o, 'Name', 'Ref', ctx)
        if att == 'Ref':
            return rid
        if att == 'Arn':
            return construct_arn(rid, resource="project", service="codebuild", slash_resource=True, ctx=ctx),
        raise Exception(f"Unknown attribute AWS::CodeBuild::Project {id} {att}")

class ManagedPolicy:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        rid = safe_get(id, o, 'ManagedPolicyName', 'Ref', ctx)
        if att == 'Ref':
            return rid
        raise Exception(f"Unknown attribute AWS::IAM::ManagedPolicy {id} {att}")

class ECRRepository:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        rid = safe_get(id, o, 'Name', 'Ref', ctx)
        if att == 'Ref':
            return rid
        if att == 'Arn':
            return construct_arn(rid, resource="repository", service="ecr", slash_resource=True, ctx=ctx)
        raise Exception(f"Unknown attribute AWS::ECR::Repository {id} {att}")

class Component:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        rid = safe_get(id, o, 'Name', ctx)
        version = safe_get(id, o, 'Version', ctx)
        build = safe_get('1', o, 'BuildVersion', 'BuildVersion', ctx)
        full = "/".join([rid, version, build])
        if att == 'Ref' or att == 'Arn':
            return construct_arn(full, resource="component", service="imagebuilder", slash_resource=True, ctx=ctx),
        raise Exception(f"Unknown attribute AWS::ImageBuilder::Component {id} {att}")

class LambdaLayerVersion:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        rid = safe_get(id, o, 'LayerName', 'Ref', ctx)
        version = safe_get("1", o, 'Version', 'Version', ctx)
        full = ":".join([rid, version])
        if att == 'Ref' or att == 'Arn':
            return construct_arn(full, resource="layer", service="lambda", ctx=ctx),
        raise Exception(f"Unknown attribute AWS::Lambda::LayerVersion {id} {att}")

class Domain:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        rid = safe_get(id, o, 'Name', 'Ref', ctx)
        domain_id = safe_get("d-xxxxxxxxxxxx", o, 'DomainId', 'DomainId', ctx)
        if att == 'Ref' or att == 'DomainId':
            return domain_id
        if att == 'Arn':
            return construct_arn(rid, resource="domain", service="sagemaker", slash_resource=True, ctx=ctx),
        raise Exception(f"Unknown attribute AWS::Lambda::LayerVersion {id} {att}")

class LaunchTemplate:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        if att == 'LatestVersionNumber':
            latest_version = safe_get("1", o, 'LatestVersionNumber', 'LatestVersionNumber', ctx)
            return latest_version
        if att == 'Ref':
            rid = safe_get("lt-" + id, o, 'TemplateId', 'TemplateID', ctx)
            return rid
        raise Exception(f"Unknown attribute AWS::EC2::LaunchTemplate {id} {att}")

class RestApi:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        rid = safe_get(id, o, 'ApiId', 'ApiId', ctx)
        if att == 'Ref':
            return rid
        if att == 'RootResourceId':
            root_id = safe_get("root-"+id, o, 'RootResourceId', 'RootResourceId', ctx)
            return root_id
        raise Exception(f"Unknown attribute AWS::EC2::LaunchTemplate {id} {att}")

class LambdaAlias:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        function_name = safe_get(id, o, 'FunctionName', ctx)
        rid = safe_get(id, o, 'Name', ctx)
        if att == 'Ref':
            full = ":".join([function_name, rid])
            return construct_arn(full, resource="function", service="lambda", slash_resource=True, ctx=ctx),
        raise Exception(f"Unknown attribute AWS::Lambda::Alias {id} {att}")

class VPC:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        if att == 'CidrBlock':
            cidr = safe_get('CIDRDEF', o, 'CidrBlock', ctx)
            return cidr
        if att == 'Ref':
            id = safe_get(id, o, 'VpcId', 'VpcId', ctx)
            return id
        raise Exception(f"Unknown attribute AWS::Lambda::Alias {id} {att}")

class Subnet:
    @staticmethod
    def get_attribute(id, o, att, ctx):
        if att == 'AvailabilityZone':
            az = safe_get('zone-a', o, 'AvailabilityZone', 'AvailabilityZone', ctx)
            return az
        if att == 'Ref':
            id = safe_get(id, o, 'SubnetId', 'SubnetId', ctx)
            return id
        raise Exception(f"Unknown attribute AWS::EC2::Subnet {id} {att}")

# some can become Generic or GenericWithArn
attribute_getters = {
    'AWS::IAM::Role': Role.get_attribute,
    'AWS::Lambda::Function': Function.get_attribute,
    'AWS::EC2::SecurityGroup': Generic.get_attribute('GroupId'),
    'AWS::S3::Bucket': Bucket.get_attribute,
    'AWS::KMS::Key': Key.get_attribute,
    'AWS::CodeDeploy::Application': Application.get_attribute,
    'AWS::IAM::InstanceProfile': InstanceProfile.get_attribute,
    'AWS::CodeDeploy::DeploymentGroup': Generic.get_attribute('DeploymentGroupName'),
    'AWS::CodeCommit::Repository': Repository.get_attribute,
    'AWS::IAM::ManagedPolicy': ManagedPolicy.get_attribute,
    'AWS::CodePipeline::Pipeline': Generic.get_attribute('Name'),
    'AWS::CodeBuild::Project': Project.get_attribute,
    'AWS::ECR::Repository': ECRRepository.get_attribute,
    'AWS::ImageBuilder::Component': Component.get_attribute,
    'AWS::ImageBuilder::DistributionConfiguration': GenericWithArn.get_attribute('Name', resource="distribution-configuration", service="imagebuilder", slash_resource=True, ref_is_arn=True),
    'AWS::ImageBuilder::ImageRecipe': GenericWithArn.get_attribute('Name', resource="image-recipe", service="imagebuilder", slash_resource=True, ref_is_arn=True),
    'AWS::SecretsManager::Secret': GenericWithArn.get_attribute('Name', service="secretsmanager", resource="secret", ref_is_arn=True, append_to_id="-abc"),
    'AWS::IAM::User': GenericWithArn.get_attribute('UserName', service='iam', resource='user', slash_resource=True),
    'AWS::IAM::Group': GenericWithArn.get_attribute('UserName', service='iam', resource='group', slash_resource=True),
    'AWS::SNS::Topic': GenericWithArn.get_attribute('TopicName', service="sns", resource="topic", ref_is_arn=True),
    'AWS::Lambda::LayerVersion': LambdaLayerVersion.get_attribute,
    'AWS::StepFunctions::StateMachine': GenericWithArn.get_attribute('StateMachineName', service="states", resource="statemachine", ref_is_arn=True),
    'AWS::Events::Rule': GenericWithArn.get_attribute('Name', service="events", resource="rule", slash_resource=True),
    'AWS::SageMaker::Domain': Domain.get_attribute,
    'AWS::AutoScaling::AutoScalingGroup': Generic.get_attribute('AutoScalingGroupName'),
    'AWS::ApiGateway::RestApi': RestApi.get_attribute,
    'AWS::ApiGateway::Deployment': Generic.get_attribute('DeploymentId'),
    'AWS::ApiGateway::Stage': Generic.get_attribute('StageName'),
    'AWS::ApiGateway::Resource': Generic.get_attribute('ResourceId'),
    'AWS::Lambda::Alias': LambdaAlias.get_attribute,
    'AWS::Logs::LogGroup': GenericWithArn.get_attribute('LogGroupName', service="logs", resource="log-group:", slash_resource=True),
    'AWS::GuardDuty::Detector': Generic.get_attribute("DetectorId"),
    'AWS::Route53::HostedZone': Generic.get_attribute('HostedZoneId'),
    'AWS::ServiceCatalog::TagOption':  Generic.get_attribute('TagOptionId'),
    'AWS::SSM::Parameter': Parameter.get_attribute,
    'AWS::SSM::Document': Generic.get_attribute('Name'),
    'AWS::SSM::MaintenanceWindow': Generic.get_attribute('MainainanceWindowId'),
    'AWS::SSM::MaintenanceWindowTarget': Generic.get_attribute('MaintainanceWindowTargetId'),
    'AWS::EC2::LaunchTemplate': LaunchTemplate.get_attribute,
    'AWS::EC2::NetworkAcl': Generic.get_attribute('Id'),
    'AWS::EC2::TransitGatewayAttachment': Generic.get_attribute('Id'),
    'AWS::EC2::DHCPOptions': Generic.get_attribute('DhcpOptionsId'),
    'AWS::EC2::InternetGateway': Generic.get_attribute('InternetGatewayId'),
    'AWS::EC2::RouteTable': Generic.get_attribute('RouteTableId'),
    'AWS::EC2::VPC': VPC.get_attribute,
    'AWS::EC2::Subnet': Subnet.get_attribute,
    'AWS::EC2::VPNGateway': Generic.get_attribute('VPNGatewayId'),
    'AWS::EC2::VPCPeeringConnection': Generic.get_attribute('Id'),
    'AWS::RDS::DBSubnetGroup': Generic.get_attribute('DBSubnetGroupName'),
}

def get_attribute(logical_id, attribute_name, ctx: TemplateParser):
    print("GETATT", logical_id)
    try:
        if logical_id in ctx.resources:
            type = ctx.resources[logical_id]["type"]
            if type.startswith('Custom::'):
                return "CustomResourceResponseTODO"
            else:
                obj = ctx.resources[logical_id]
                if type in attribute_getters:
                    return attribute_getters[type](logical_id, obj, attribute_name, ctx)
                else:
                    raise Exception(f"attribute not found {type} {logical_id} {attribute_name}")
    except Exception as e:
        raise Exception(f"attribute not found {type} {logical_id} {attribute_name}")