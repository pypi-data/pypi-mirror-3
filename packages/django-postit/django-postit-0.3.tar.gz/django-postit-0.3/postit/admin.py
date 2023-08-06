from django.contrib import admin

from postit.models import PostIt, UserProfile

class PostItAdmin(admin.ModelAdmin):
    list_filter = ['user_to']
    list_display = ('title','user_to')

class UserProfileAdmin(admin.ModelAdmin):
	#list_filter = ['user','color',]
	list_display = ('user', 'color')
	list_editable = ('color',)
	
	def color(self, obj):
            print obj
	    print dir(obj)

	    if obj.colorcode:
                return u'<div style="background-color:%(colorcode)s;width:12px;height:12px;display:inline-block;"></div> %(colorcode)s' % {'colorcode': obj.colorcode};
            return ''
	color.allow_tags = True

admin.site.register(PostIt, PostItAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
