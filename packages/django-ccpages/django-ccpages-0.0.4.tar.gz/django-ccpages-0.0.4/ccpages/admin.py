from django.contrib import admin
from ccpages.models import Page, PageImage, PageAttachment
from ccpages.forms import PageAdminForm


class PageImageInline(admin.TabularInline):
    model = PageImage


class PageAttachmentInline(admin.TabularInline):
    model = PageAttachment


class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    search_fields = (
            'title',
            'content',)
    list_filter = (
            'status',)
    list_display = (
            'title',
            'order',
            'status')
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
            'fields': ('slug',
                        'order',
                        'password',),
            'classes': ('collapse', 'other')
        })
    )


admin.site.register(Page, PageAdmin)
