from django.db import models
from cms.models import CMSPlugin
from django.template.defaultfilters import slugify

class FAQList(models.Model):
    title = models.TextField()
    language = models.CharField(max_length=128, blank=True)
    order = models.IntegerField(default=100)

    class Meta:
        ordering = ['order', 'title']

    def verbose_title(self):
        if self.language:
            return u'[%s]%s' % (self.language, self.title)
        else:
            return self.__unicode__()

    def __unicode__(self):
        return u'%s' % self.title

    def get_slug(self):
        return slugify(self.title)

class FAQEntry(models.Model):
    faq_list = models.ForeignKey(FAQList, related_name="faq_entries")
    question = models.TextField()
    answer = models.TextField()
    order = models.IntegerField(default=100)

    class Meta:
        ordering = ['order', 'question']

    def __unicode__(self):
        return u'%s' % self.question

class FAQPlugin(CMSPlugin):
    faq_list = models.ForeignKey(FAQList)

    def copy_relations(self, oldinstance):
        self.faq_list = oldinstance.faq_list

class FAQListPlugin(CMSPlugin):
    faq_list = models.ManyToManyField(FAQList)

    def copy_relations(self, oldinstance):
        self.faq_list = oldinstance.faq_list