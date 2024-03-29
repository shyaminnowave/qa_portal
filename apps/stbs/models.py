from django.db import models
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords
# Create your models here.


class Language(TimeStampedModel):
    language_name = models.CharField(max_length=100)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s' % self.language_name


class STBManufacture(TimeStampedModel):
    name = models.CharField(max_length=200)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s' % self.name


class Natco(TimeStampedModel):

    country = models.CharField(max_length=200)
    natco = models.CharField(max_length=10)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s' % self.country


class NactoManufactureLanguage(TimeStampedModel):
    natco = models.ForeignKey(Natco, on_delete=models.CASCADE)
    device_name = models.ForeignKey(STBManufacture, on_delete=models.CASCADE)
    language_name = models.ForeignKey(Language, on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s' % self.natco.country
