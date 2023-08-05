from django import template
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from dishes.models import Menu

register = template.Library()

class GetMenusNode(template.Node):
    """
    Retrieves a list of active menus
    """
    def __init__(self, count, varname):
        self.count = count
        self.varname = varname

    def render(self, context):
        if self.count:
            try:
                menus = Menu.active_objects.all()[:self.count]
            except TypeError:
                menus = []
        else: menus = Menu.active_objects.all()

        context[self.varname] = menus 
        return ''

def get_active_menus(parser, token):
    """
    Retrieves a list of active menus 

    {% get_active_menus as menus %}
    {% get_active_menus 4 as menus %}
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert (argc == 3 and args[1] == 'as') or (argc == 4 and args[2] == 'as')
    except AssertionError:
        raise template.TemplateSyntaxError('get_active_menus syntax: {% get_active_menus [|integer] as varname %}')

    count = varname = None
    if argc == 3: t, a, varname = args
    elif argc == 4: t, count, a, varname = args

    return GetMenusNode(count=count, varname=varname)

register.tag(get_active_menus)
