from cmsplugin_multiple_faq.models import FAQEntry, FAQList
from django.contrib import admin

class FAQEntryInline(admin.TabularInline):
    model = FAQEntry

class FAQListAdmin(admin.ModelAdmin):
    list_display = ('verbose_title', 'order')
    inlines=[FAQEntryInline]

admin.site.register(FAQList, FAQListAdmin)