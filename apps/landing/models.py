from django.db import models
from django.utils.translation import ugettext_lazy as _


class LexiconEntry(models.Model):

    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('revise', _('Revise')),
        ('ready', _('Ready')),
    )

    term = models.CharField(_('term'), max_length=255)
    slug = models.SlugField()
    abbreviation = models.CharField(_('abbreviation'), max_length=20, null=True, blank=True)
    description = models.TextField(_('description'), null=True, blank=True)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    published = models.BooleanField(_('published'), default=False)

    class Meta:
        ordering = ('term',)
        verbose_name_plural = _("lexicon entries")

    def __str__(self):
        string = "{}".format(self.term)
        if self.abbreviation:
            string += " ({})".format(self.abbreviation)
        return string


class PressEntry(models.Model):
    title = models.CharField(max_length=50)
    date = models.DateField()
    headline = models.CharField(max_length=140)
    details = models.TextField(null=True, blank=True)
    link = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ('-date',)
        verbose_name_plural = _("press entries")

    def __str__(self):
        return "{}".format(self.title)
