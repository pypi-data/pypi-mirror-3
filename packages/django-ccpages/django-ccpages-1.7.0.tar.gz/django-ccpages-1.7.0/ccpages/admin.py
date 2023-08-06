from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from ccpages.models import Page, PageImage, PageAttachment
from ccpages.forms import PageAdminForm


class PageImageInline(admin.TabularInline):
    model = PageImage


class PageAttachmentInline(admin.TabularInline):
    model = PageAttachment


class PageAdmin(MPTTModelAdmin):
    form = PageAdminForm
    search_fields = (
            'title',
            'content',)
    list_filter = (
            'status',)
    list_display = (
            'title',
            'status',
            'order',)
    list_editable = (
            'order',
            'status',)
    save_on_top = True
    inlines = [
            PageImageInline,
            PageAttachmentInline]
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('parent',
                        'status',
                        'title',
                        'content',),
            'classes': ('content',)
        }),
        ('Other Stuff', {
            'fields': ( 'layout',
                        'password',
                        'slug',
                        'order',),
            'classes': ('collapse', 'other')
        })
    )

admin.site.register(Page, PageAdmin)
