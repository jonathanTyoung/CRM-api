from django.db import models
from .tags import Tag
from .contacts import Contact

class ContactTag(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)