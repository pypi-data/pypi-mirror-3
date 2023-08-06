from django import template
from ..models import Menu





register = template.Library()

def build_menu(parser, token):
    """
    {% menu menu_name %}
    """
    try:
        tag_name, menu_name = token.split_contents()        
    except:
        raise template.TemplateSyntaxError, "%r tag requires exactly one argument" % token.contents.split()[0]
    return MenuObject(menu_name)

class MenuObject(template.Node):
    def __init__(self, menu_name):
        self.menu_name = menu_name

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
        
        try:
            m = Menu.objects.get(name=self.menu_name)
            return m.render()
        except Menu.DoesNotExist:
            return "<!-- Menu not found -->"
register.tag('menu', build_menu)