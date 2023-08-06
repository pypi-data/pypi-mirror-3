from django.db import models
from django.utils.translation import ugettext_lazy as _
from transmeta import TransMeta
from django.template.loader import render_to_string



 
# -------------------------------------------------------------------------------------------


class Menu(models.Model):
    __metaclass__ = TransMeta
    name = models.CharField(_('name'), max_length=100)
    label = models.CharField(_('label'), max_length=100)
    slug = models.SlugField(_('id'))
    description = models.TextField(_('description'), blank=True, null=True)

    class Meta:
        translate = ('label', )
    
    def __unicode__(self):
        return u"%s" % self.label
        
    
    def render(self):        
        sm = self.submenus.all()
        return render_to_string('menu.html', {'name': self.name, 'submenus': sm, 'max_depth': 0 })
        
 
# -------------------------------------------------------------------------------------------   
    
class MenuElement(models.Model):
    __metaclass__ = TransMeta

    label = models.CharField(_('label'), max_length=100)
    order = models.IntegerField(_('Order'))
    url = models.CharField(_('URL'), max_length=100, help_text=_('URL o URI al contenido, ej: /nosotros/ or http://foo.com/'))
    login_required = models.BooleanField(_('Solo usuarios registrados'),blank=True)
    
    
    class Meta:
        verbose_name = _('elemento del menu')
        verbose_name_plural = _('elementos del menu')
        translate = ('label', )
        
    def depth(self):
        return 0
        
    def render(self):
        sm = self.submenus.all()
        return render_to_string('submenu.html', {'submenus': sm })
        
    def __unicode__(self):
        try:
            return u"%s" % self.childmenuelement
        except:
            try:
                return u"%s" % self.parentmenuelement
            except:
                return u"%s" % self.label
            
            
            
    def top_menu(self):
        try:
            return u"%s" % self.childmenuelement.top_menu()
        except:
            try:
                return u"%s" % self.parentmenuelement.top_menu()
            except:
                return u""
        
        
   
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
    
    class Meta:
        verbose_name = _('elemento del menu')
        verbose_name_plural = _('elementos del menu')
    
    
    def depth(self):
        try:
            return self.parent.childmenuelement.depth() + 1
        except:
            return 2
        
    
    def __unicode__(self):
        return u"%s > %s" % (self.parent, self.label)
    
    
    def top_menu(self):
        return self.parent.top_menu()
        
    
class ParentMenuElement (MenuElement):
    menu = models.ForeignKey('Menu', related_name="submenus")
    
    class Meta:
        verbose_name = _('elemento del menu')
        verbose_name_plural = _('elementos del menu')
    
    
    def depth(self):
        return 1
    
    
    def __unicode__(self):
        return u"%s > %s" % (self.menu, self.label)  
    
    def top_menu(self):
        return self.menu.name
