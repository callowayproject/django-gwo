from django import template
import settings
from gwo.models import GwoExperiment, GwoSection

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


class GwoSectionNode(template.Node):
    def __init__(self, section_name, start):
        self.section_name = template.Variable(section_name)
        self.start = start
    
    def render(self, context):
        try:
            section_name = resolve_or_literal(self.section_name, context)
            exp = context.get('gwo_experiment')
            section = exp.gwosection_set.get(title=section_name)
            if self.start:
                return section.begin_script
            else:
                return section.end_script
        except GwoSection.DoesNotExist:
            raise template.TemplateSyntaxError("Can't find section %s in experiment %s" % (section_name, exp.title))


class GwoExperimentNode(template.Node):
    def __init__(self, experiment_name):
        self.experiment_name = template.Variable(experiment_name)
    
    def render(self, context):
        try:
            exp_name = resolve_or_literal(self.experiment_name, context)
            exp = GwoExperiment.objects.get(title=exp_name)
        except GwoExperiment.DoesNotExist:
            raise template.TemplateSyntaxError("Can't find experiment named %s" % exp_name)
        context['gwo_experiment'] = exp
        return ''


@register.tag
def set_experiment(parser, token):
    """
    Set a variable ``gwo_experiment`` within the context to the experiment.
    
    {% set_experiment "Experiment Name" %}
    """
    bits = token.split_contents()
    if len(bits) == 2:
        return GwoExperimentNode(bits[1])
    else:
        raise template.TemplateSyntaxError("%r should use the form {%% %r experimentname %%}" % (bits[0], bits[0]))

@register.tag
def gwo_start_section(parser, token):
    try:
        tag_name, gwo_section = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a GWO section name" % token.contents.split()[0]
    return GwoSectionNode(gwo_section, start=True)

@register.tag
def gwo_end_section(parser, token):
    try:
        tag_name, gwo_section = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a GWO section name" % token.contents.split()[0]
    return GwoSectionNode(gwo_section, start=False)

@register.inclusion_tag('gwo/trackclick_script.html', takes_context=True)
def trackclick_script(context):
    import re
    regex = re.compile(r'(^try.+catch\(err\){})', re.MULTILINE|re.DOTALL)
    exp = context.get('gwo_experiment', '')
    if exp:
        c_script = regex.search(exp.conversion_script).group(0)
    else:
        c_script = ''
    return {
        'conversion_script': c_script
    }

@register.inclusion_tag('gwo/trackclick.html')
def trackclick():
    return {}