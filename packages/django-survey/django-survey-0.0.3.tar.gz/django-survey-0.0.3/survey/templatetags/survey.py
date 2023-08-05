from django import template
from survey.models import Survey

register = template.Library()

@register.filter
def has_answered(request, survey):
    if not hasattr(request, 'session'): return False
    return survey.has_answers_from(request.session.session_key)

@register.filter
def can_view_answers(user, survey):
    return survey.answers_viewable_by(user)

@register.filter_function
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)

class GetSurveyNode(template.Node):
    '''
        Lookup a survey via a slug and add it to the page context.
        Return the context.
    '''
    def __init__(self, slug, context_var):
        self.obj=Survey.objects.get(slug=slug)
        self.context_var=context_var

    def render(self, context):
        context[self.context_var]=self.obj
        return ''

def do_get_survey(parser, token):
    '''
        Retrieves a survey by slug
        {% get_survey <slug> as <template var> %}
     '''
    try:
        bits = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(_('tag requires exactly two arguments'))
    if len(bits) != 4:
        raise template.TemplateSyntaxError(_('tag requires exactly three arguments'))
    if bits[2] != 'as':
        raise template.TemplateSyntaxError(_("second argument to tag must be 'as'"))
    return GetSurveyNode(bits[1], bits[3])

register.tag('get_survey', do_get_survey)
