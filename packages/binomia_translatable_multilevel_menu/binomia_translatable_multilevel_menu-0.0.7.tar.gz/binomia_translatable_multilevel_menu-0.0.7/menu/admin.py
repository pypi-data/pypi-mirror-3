from django.contrib import admin


from models import Menu, MenuElement, ParentMenuElement, ChildMenuElement

class ParentMenuElementInline(admin.TabularInline):
    model = ParentMenuElement
    #fields = ('nombre', 'orden', 'url', 'login_required')
    extra = 0
    #fk_name ='literal'
    
class ChildMenuElementInline(admin.TabularInline):
    model = ChildMenuElement
    fk_name = 'parent'
    #fields = ('nombre', 'orden', 'url', 'login_required')
    extra = 0
    #fk_name ='literal'
    
class MAdmin(admin.ModelAdmin):
    inlines = [ParentMenuElementInline,]
    
class EMAdmin(admin.ModelAdmin):
    inlines = [ChildMenuElementInline,]
    


admin.site.register(Menu, MAdmin)    
admin.site.register(MenuElement, EMAdmin)    
#admin.site.register(ParentMenuElement)    
#admin.site.register(ChildMenuElement)