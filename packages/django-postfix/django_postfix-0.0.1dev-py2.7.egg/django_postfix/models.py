from django.db import models
from django.utils.translation import ugettext_lazy as _

class Domain(models.Model):
    domain = models.CharField(_('domain'), max_length=128, unique=True)
    description = models.CharField(_('description'), max_length=128, blank=True, null=True)
    active = models.BooleanField(_('is active'), default=False)
    aliases = models.BooleanField(_('allow aliases'), default=False)
    mailboxes = models.BooleanField(_('has mailboxes'), default=False)
    backupmx = models.BooleanField(_('backup MX records'), default=False)
    transport = models.CharField(_('transport'), max_length=128, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'domains'

    def __unicode__(self):
        return u'%s' % self.domain

class Mailbox(models.Model):
    domain = models.ForeignKey(Domain)
    username = models.CharField(_('username'), max_length=255, unique=True,
        help_text=_('Required. 255 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'))
    password = models.CharField(_('password'), max_length=128)
    maildir = models.CharField(_('mail directory'), max_length=128)
    quote = models.PositiveIntegerField(_('quote'), default=0)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mailboxes'
        verbose_name = 'mail box'
        verbose_name_plural = 'mail boxes'
        unique_together = ('domain', 'username')

    def __unicode__(self):
        return u'%s' % self.username

class Alias(models.Model):
    alias = models.CharField(max_length=128)
    mailbox = models.ForeignKey(Mailbox)
    domain = models.ForeignKey(Domain, null=True, blank=True)
    active = models.BooleanField(_('is active'), default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'aliases'
        verbose_name = 'alias'
        verbose_name_plural = 'aliases'
        unique_together = ('alias', 'mailbox')

    def __unicode__(self):
        return u'%s for %s' % (self.alias, self.mailbox.username)
