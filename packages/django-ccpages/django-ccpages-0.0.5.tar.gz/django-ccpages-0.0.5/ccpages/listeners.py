import hashlib
from markdown import markdown

def set_content_rendered(sender, instance, **kwargs):
    """When a page is saved the content is rendered out
    onto the model and saved to avoid the overhead of doing
    it on every request"""

    instance.content_rendered = markdown(instance.content)

def set_hash(sender, instance, **kwargs):
    """If a page has a password then create a hash for it"""

    if instance.password is None:
        return None

    instance.hash = hashlib.sha1(instance.password).hexdigest()
