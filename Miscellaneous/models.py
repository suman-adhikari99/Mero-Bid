from django.db import models

# Create your models here.

class Testimonals(models.Model):
    description=models.TextField()
    photo=models.FileField()
    name=models.CharField(max_length=254)

    def __str__(self):
        return  str(self.name)



class Clients(models.Model):
    photo=models.FileField()
    name=models.CharField(max_length=254)

    def __str__(self):
        return  str(self.name)
