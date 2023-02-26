import pytest
from resolve import TemplateParser, TemplateContext
from getatt_dummy import get_attribute

'''
tests to make:
- ssm parameter test
- missing parameter with use_default_parameter_values
- missing ssm parameter input
- {{resolve:ssm}} in parameters??
- novalue in a list
- get attribute from non existant resource
'''
def test_other():
    pass

def test_generic(input_expected):
    context=TemplateContext(
        "123456789",
        "eu-central-1",
        "MyStack",
        parameters=input_expected.get("parameters", {}),
        ssm_parameters=input_expected.get("ssm_parameters", {}),
        exports=input_expected.get("exports", {}),
    )
    if "error" in input_expected["expected"]:
        with pytest.raises(Exception, match=input_expected["expected"]["error"]):
            p = TemplateParser(
                context,
                input_expected["input"],
                use_parameter_defaults=input_expected.get("use_parameter_defaults", True),
                get_attribute=get_attribute
            )
            p.resolve()
    else:
        p = TemplateParser(
            context,
            input_expected["input"],
            use_parameter_defaults=input_expected.get("use_parameter_defaults", True),
            get_attribute=get_attribute
        )
        p.resolve()     
    if "data" in input_expected["expected"]:
        assert p.data == input_expected["expected"]["data"]
    if "parameters" in input_expected["expected"]:
        assert p.parameters == input_expected["expected"]["parameters"]
    if "conditions" in input_expected["expected"]:
        assert p.conditions == input_expected["expected"]["conditions"]
