from django import template
import settings
from gwo.models import GwoExperiment

register = template.Library()

def resolve_or_literal(variable, context):
    """
    Resolve the variable within the context, or return the literal value passed
    """
    try:
        var = variable.resolve(context)
    except template.VariableDoesNotExist:
        var = variable.literal or variable.var
    return var

def _get_context_from_exp_name(experiment_name):
    """
    Get an experiment by its name. Used for several inclusion templates
    """
    try:
        exp = GwoExperiment.objects.get(slug=experiment_name)
    except GwoExperiment.DoesNotExist:
        exp = None
    return template.Context({'experiment': exp, 'gwo_account': settings.GWO_ACCOUNT})

class GwoInclusionNode(template.Node):
    def __init__(self, tmpl, experiment_name):
        self.experiment_name = template.Variable(experiment_name)
        self.template = tmpl
    
    def render(self, context):
        from django.template.loader import get_template
        exp_name = resolve_or_literal(self.experiment_name, context)
        ctxt = _get_context_from_exp_name(exp_name)
        
        tmpl = get_template(self.template)
        return tmpl.render(ctxt)

def gwo_generic_compiler(parser, token, template):
    try:
        tag_name, gwo_exp = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a GWO experiment name" % token.contents.split()[0]
    return GwoInclusionNode(template, gwo_exp)

@register.tag
def gwo_control_script(parser, token):
    return gwo_generic_compiler(parser, token, "gwo/gwo_control_script.html")

@register.tag
def gwo_tracking_script(parser, token):
    return gwo_generic_compiler(parser, token, "gwo/gwo_tracking_script.html")

@register.tag
def gwo_conversion_script(parser, token):
    return gwo_generic_compiler(parser, token, "gwo/gwo_conversion_script.html")
