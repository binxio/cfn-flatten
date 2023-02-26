# cfn-flatten

This python 3.11 script can "flatten" a CloudFormation template. 

The class `TemplateParser` can be used as follows:

```python
import json
from resolver import TemplateParser, TemplateContext
from getatt_dummy import get_attribute

with open("template.json", "r") as f:
    template_json=json.load(f)
context = TemplateContext(
    "123456789012",
    "eu-central-1",
    "MyStack",
    parameters={
        "CidrBlock": "192.168.0.0/24"
    }
)
parser = TemplateParser(
    "123456789012",   # account where the stack is deployed
    "eu-central-1",   # region where the stack is deployed
    "MyStack",        # name of the stack
    template_json,
    get_attribute=get_attribute
)
parser.resolve()
with open("output.json", "w") as f:
    template_json=json.dump(parser.data)
```

Example usage:

```json
{
    "Parameters": {
        "CidrBlock": {
            "Type": "String"
        }
    },
    "Resources": {
        "MyRole": {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "RoleName": {
                    "Fn::Select": [
                        0,
                        {
                            "Fn::Cidr": [
                                {
                                    "Ref": "CidrBlock"
                                },
                                "6",
                                "5"
                            ]
                        }
                    ]
                }
            }
        }
    }
}
```

resolves to:

```json
{
    "Resources": {
        "MyRole": {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "RoleName": "192.168.0.0/27"
            }
        }
    }
}
```

If you want to use `yaml` instead of `json` use the package `cfn-flip`.

# Attributes

Currently no intelligent attribute value generator is in place. The project
only has the `getatt_dummy.py` script which replaces all attributes with an
`xml` comment string. This is for testing purposes only.

Here are two ideas for create usefull attribute getters:

- generate the attribute values from the available code (inventing names, ids and other stuff on the fly)
- get the actual value from deployed resources using api calls

Since it is quit the undertaking to create these attribute getter for all available AWS resources
this is logically separated from the parser. An initial version of a generator is in `getatt.py` but
it is still under developement and the internals might change drastically.

You can specify your own custom attribute getter in the constructor of the `TemplateParser`:

```python
from resolver import TemplateParser

def my_get_attribute(logical_id, attribute_name, ctx: TemplateParser):
    # perform your magic here
    return "AttributeValue"

parser = TemplateParser(
    "123456789012",
    "eu-central-1",
    "MyStack",
    template_json,
    get_attribute=my_get_attribute
)
```

# Parameters

If you specify `use_default_parameter_values=True` the default values specified in the
template will be used if a parameter is not specified in the `TemplateContext`. When
`use_default_parameter_values=False` and a parameter reference is encountered that is
not specified in the `TemplateContext` an exception will be raised.

For ssm parameters the default refers to the name of the ssm parameter to use. You can
specify ssm parameters by specifying `ssm_parameters` when creating the `TemplateContext`.

# Imports (and exports)

Imports are values that are exported by other CloudFormation templates using
`Fn::ImportValue`. You can add values to import to `exports` of `TemplateContext`.

The exports of a temmplate should be resolved at the end.

# Why

Why would you want to do this you might ask. Well for several reasons actually. 
When all the intrinsics and references are resolved the CloudFormation becomes
very simple. Just the resources that will be deployed and their properties.

Some thing become a whole lot easier to create without the presense of intrinsics:

- Static analysis of the CloudFormation templates
- Making cfn-guard rules
- Transpiling CloudFormation to another IaC language like CDK or terraform
- Detecting drift with the actual resources deployed
- Finding circular references between templates

# How

The CloudFormation template is gruadually parsed by the compact code in `resolve.py`.

The following steps are executed:

- exract the mapings
- get the parameters from the context (use defaults and ssm parameters)
- resolve all condition
- remove resources based on condition
- go over the data resolving intrinsics
- cleanup template (only resources, expoprts are kept)

# Setup

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

# Testing

Test cases are in `tests/data` and they are formatted as json files.

"ssm_parameters" is input for ssm parameters
"parameters" is input for normal parameters
"input" is the input template
"expected"
    "data" is the resolved template
    "paramaters" are the resolved parameters
    "conditions" are the resolved conditions

Unit tests

`pytest`

Test coverage

`pytest --cov-report term-missing --cov=. tests/ --cov-branch`

