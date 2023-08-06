from django.db import models
from django.db.models.signals import pre_delete, post_delete, post_save, pre_save

class RailsModel(models.Model):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(RailsModel, self).__init__(*args, **kwargs)
        self.connect_hooks(self.__class__)

    @classmethod
    def all(cls):
        return cls.objects.all()

    @classmethod
    def find(cls, id):
        return cls.objects.get(id=id)

    @classmethod
    def first(cls, count=None):
        objects = cls.objects.all().order_by('id')
        return objects[0] if not count else objects[:count]

    @classmethod
    def last(cls, count=None):
        objects = cls.objects.all().order_by('-id')
        return objects[0] if not count else objects[:count]

    def connect_hooks(self, model):
        post_delete.connect(self.post_delete_hook, sender=model)
        pre_delete.connect(self.pre_delete_hook, sender=model)
        pre_save.connect(self.pre_save_hook, sender=model)
        post_save.connect(self.post_save_hook, sender=model)

    def pre_save_hook(self, sender, **kwargs):
        if kwargs['instance'].id == None:
            self.call_hook(sender, 'before_create', kwargs['instance'])
        else:
            self.call_hook(sender, 'before_update', kwargs['instance'])
        self.call_hook(sender, 'before_save', kwargs['instance'])

    def post_save_hook(self, sender, **kwargs):
        if kwargs['created']:
            self.call_hook(sender, 'after_create', kwargs['instance'])
        else:
            self.call_hook(sender, 'after_update', kwargs['instance'])
        self.call_hook(sender, 'after_save', kwargs['instance'])

    def pre_delete_hook(self, sender, **kwargs):
        self.call_hook(sender, 'before_delete', kwargs['instance'])

    def post_delete_hook(self, sender, **kwargs):
        self.call_hook(sender, 'after_delete', kwargs['instance'])

    def call_hook(self, sender, method, instance):
        func = getattr(sender, method, None)
        if callable(func):
            func(instance)

