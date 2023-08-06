from django.db.models.signals import pre_delete, post_delete, post_save, pre_save

def connect_hooks(model):
    post_delete.connect(post_delete_hook, sender=model)
    pre_delete.connect(pre_delete_hook, sender=model)
    pre_save.connect(pre_save_hook, sender=model)
    post_save.connect(post_save_hook, sender=model)

def pre_save_hook(sender, **kwargs):
    if kwargs['instance'].id == None:
        call(sender, 'before_create', kwargs['instance'])
    else:
        call(sender, 'before_update', kwargs['instance'])
    call(sender, 'before_save', kwargs['instance'])

def post_save_hook(sender, **kwargs):
    if kwargs['created']:
        call(sender, 'after_create', kwargs['instance'])
    else:
        call(sender, 'after_update', kwargs['instance'])
    call(sender, 'after_save', kwargs['instance'])

def pre_delete_hook(sender, **kwargs):
    call(sender, 'before_delete', kwargs['instance'])

def post_delete_hook(sender, **kwargs):
    call(sender, 'after_delete', kwargs['instance'])

def call(sender, method, instance):
    func = getattr(sender, method, None)
    if callable(func):
        func(instance)
