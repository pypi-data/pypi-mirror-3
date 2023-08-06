from django.db import models as m

# Create your models here.

class M(m.Model):
    a = m.CharField(max_length="200")
    b = m.TextField()
