from django.contrib import admin
from django_postfix.models import Domain, Mailbox, Alias

class AliasInline(admin.TabularInline):
    model = Alias
    exclude = ['domain', ]
    extra = 0

class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'active', 'aliases', 'mailboxes', 'backupmx')
    search_fields = ('domain', 'description')

class MailboxAdmin(admin.ModelAdmin):
    search_fields = ('username',)
    list_display = ('username', 'maildir', 'quote')
    list_filter = ('domain',)
    date_hierarchy = 'created'
    inlines = [AliasInline]

admin.site.register(Domain, DomainAdmin)
admin.site.register(Mailbox, MailboxAdmin)
admin.site.register(Alias)
