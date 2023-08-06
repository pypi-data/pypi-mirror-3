import os
from datetime import datetime
from django.utils.encoding import smart_str
from markdown2 import markdown
from django.template.defaultfilters import striptags, truncatewords
from ccnews import settings as c_settings

def set_attachment_title(sender, instance, **kwargs):
    """If a file attachment is saved and it does not
    have a title then one will be generated from it's filename"""
    if not instance.title:
        instance.title = os.path.basename(instance.src.path)

def set_created(sender, instance, **kwargs):
    """Sets the created date into an instance if it's
    created data is none """
    if instance.created is None:
        instance.created = datetime.now()

def set_excerpt(sender, instance, **kwargs):
    """Provided with an instance of an article this sets a
    plain text excerpt on the instance.
    
    The length of the output in words can be controlled
    from the c_settings.CCNEWS_SNIPPET_LENGTH setting.
    """
    excerpt = markdown(instance.content)
    excerpt = striptags(excerpt)
    excerpt = truncatewords(excerpt, c_settings.CCNEWS_EXCERPT_LENGTH)
    instance.excerpt = smart_str(excerpt)

def set_content_rendered(sender, instance, **kwargs):
    """Renders the content out to avoid taking the 
    hit on rendering for every view"""
    content_rendered = markdown(
                        instance.content,
                        extras=[
                            'header-ids',
                            'smarty-pants'])
    instance.content_rendered = smart_str(content_rendered)
