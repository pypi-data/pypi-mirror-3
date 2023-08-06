# -*- coding: utf-8 -*-
import os
from django.utils.encoding import smart_str
import hashlib
from markdown2 import markdown

def set_attachment_title(sender, instance, **kwargs):
    """If a file attachment is saved and it does not
    have a title then one will be generated from it's filename"""
    if not instance.title:
        instance.title = os.path.basename(instance.src.path)

def set_content_rendered(sender, instance, **kwargs):
    """When a page is saved the content is rendered out
    onto the model and saved to avoid the overhead of doing
    it on every request"""
    content_rendered = markdown(
                        instance.content,
                        extras=[
                            'header-ids',
                            'smarty-pants'])
    instance.content_rendered = smart_str(content_rendered)





def set_hash(sender, instance, **kwargs):
    """If a page has a password then create a hash for it"""

    if instance.password is None:
        return None

    instance.hash = hashlib.sha1(instance.password).hexdigest()
