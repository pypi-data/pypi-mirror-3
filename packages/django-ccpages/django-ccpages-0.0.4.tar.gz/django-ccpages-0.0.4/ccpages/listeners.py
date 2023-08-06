import hashlib

def create_hash(sender, instance, **kwargs):
    """If a page has a password then create a hash for it"""
    if instance.password is None:
        return None
    instance.hash = hashlib.sha1(instance.password).hexdigest()
