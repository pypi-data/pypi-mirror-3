from django.db import models
from django.utils.translation import ugettext_lazy as _
from transmeta import TransMeta
from django.template.loader import render_to_string

 
# -------------------------------------------------------------------------------------------


class Menu(models.Model):
    __metaclass__ = TransMeta

    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('id'))
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        translate = ('name', )
    
    def __unicode__(self):
        return "%s" % self.name
        
    
    def render(self):        
        sm = self.submenus.all()
        return render_to_string('menu.html', {'submenus': sm, 'max_depth': 0 })
        
 
# -------------------------------------------------------------------------------------------   
    
class MenuElement(models.Model):
    __metaclass__ = TransMeta

    name = models.CharField(_('name'), max_length=100)
    order = models.IntegerField(_('Order'))
    url = models.CharField(_('URL'), max_length=100, help_text=_('URL o URI al contenido, ej: /nosotros/ or http://foo.com/'))
    
    
    class Meta:
        #verbose_name = _('elemento del menu')
        #verbose_name_plural = _('elementos del menu')
        translate = ('name', )
        
    def depth(self):
        return 0
        
    def render(self):
        sm = self.submenus.all()
        return render_to_string('menu.html', {'submenus': sm })
        
    def __unicode__(self):
        try:
            return "%s" % self.childmenuelement
        except:
            return "%s" % self.name
        
        
   
# -------------------------------------------------------------------------------------------       
"""
from menus.menuAnidado.models import Menu, MenuElement, ParentMenuElement, ChildMenuElement
m = Menu.objects.get(name_es="HORIZONTAL")
m.render()
pme = ParentMenuElement.objects.get(pk=1)
cm = ChildMenuElement.objects.get(pk=3)
cm.list()


"""

# -------------------------------------------------------------------------------------------


class ChildMenuElement (MenuElement):
    parent = models.ForeignKey('MenuElement', related_name="submenus")
    
    
    def depth(self):
        try:
            return self.parent.childmenuelement.depth() + 1
        except:
            return 2
        
    
    def __unicode__(self):
        return "%s > %s" % (self.parent, self.name)
    
    
        
    
class ParentMenuElement (MenuElement):
    menu = models.ForeignKey('Menu', related_name="submenus")
    
    
    def depth(self):
        return 1
    
    
    
