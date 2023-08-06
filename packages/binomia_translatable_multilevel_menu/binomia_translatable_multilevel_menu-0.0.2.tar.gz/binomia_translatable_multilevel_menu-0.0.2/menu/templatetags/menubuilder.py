from django import template
from ..models import Menu





register = template.Library()

def build_menu(parser, token):
    """
    {% menu menu_name %}
    """
    try:
        tag_name, menu_name, level = token.split_contents()        
    except:
        raise template.TemplateSyntaxError, "%r tag requires exactly two argument" % token.contents.split()[0]
    return MenuObject(menu_name, level)

class MenuObject(template.Node):
    def __init__(self, menu_name, level):
        self.menu_name = menu_name
        self.level = level

    def render(self, context):        
        try:
            """
            current_path = template.resolve_variable('request.path', context)        
            user = template.resolve_variable('request.user', context)       
            context['menuitems'] = get_items(self.menu_name, current_path, user)
            -
            """
        except:
            pass
        
        
        m = Menu.objects.get(name_es="HORIZONTAL")
        
        print m
        return m.render()
register.tag('menu', build_menu)