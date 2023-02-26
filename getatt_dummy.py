from resolve import TemplateParser

def get_attribute(logical_id, attribute_name, ctx: TemplateParser):
    if logical_id in ctx.resources:
        return f"<!--{logical_id}.{attribute_name}-->"
    raise Exception(f"attribute not found {logical_id} {attribute_name}")