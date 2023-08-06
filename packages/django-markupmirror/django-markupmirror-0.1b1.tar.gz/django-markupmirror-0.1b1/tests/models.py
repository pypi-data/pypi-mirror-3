from django import forms
from django.db import models

from feincms.module.page.models import Page

from markupmirror.feincms.models import MarkupMirrorContent
from markupmirror.fields import MarkupMirrorField


class Post(models.Model):
    title = models.CharField(max_length=50)
    body = MarkupMirrorField('post body')
    comment = MarkupMirrorField(
        escape_html=True, default_markup_type='markdown')
    markdown_field = MarkupMirrorField(markup_type='markdown')

    def __unicode__(self):
        return self.title


class Abstract(models.Model):
    content = MarkupMirrorField()

    class Meta:
        abstract = True


class Concrete(Abstract):
    pass


class PostForm(forms.ModelForm):
    class Meta:
        model = Post


Page.register_templates({
    'key': 'page',
    'title': 'Page template',
    'path': 'feincms_page.html',
    'regions': (
        ('main', 'Main region'),
        ),
})

# register *only* this contenttype
Page.create_content_type(MarkupMirrorContent)
