from django.db import models
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords
# Create your models here.


class Language(TimeStampedModel):
    language_name = models.CharField(max_length=100)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s' % self.language_name

    class Meta:
        permissions = [
            ("view_language_option", "Can View Language Option List")
        ]


class STBManufacture(TimeStampedModel):
    name = models.CharField(max_length=200)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s' % self.name

    class Meta:
        permissions = [
            ("view_stb_option", "Can View stb Option List")
        ]


class Natco(TimeStampedModel):

    country = models.CharField(max_length=200)
    natco = models.CharField(max_length=10)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s' % self.country

    class Meta:
        permissions = [
            ("view_natco_option", "Can View natco Option List")
        ]


class NactoManufactureLanguage(TimeStampedModel):
    natco = models.ForeignKey(Natco, on_delete=models.CASCADE)
    device_name = models.ForeignKey(STBManufacture, on_delete=models.CASCADE)
    language_name = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='natco_maufacture')
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s - %s' % (self.natco.natco, self.language_name.language_name)

    class Meta:
        permissions = [
            ("view_natco_manufacture_option", "Can View Natco Manufacture Language Option List")
        ]


class STBInfo(TimeStampedModel):
    node_id = models.CharField(max_length=200, default='')


class STBSRelease(TimeStampedModel):

    stb_node = models.ForeignKey(STBInfo, on_delete=models.CASCADE)
    natco = models.CharField(max_length=255, default='')
    stb_build_info = models.CharField(max_length=255, default='')
    stb_release= models.CharField(max_length=255, default='')
    stb_firmware = models.CharField(max_length=255, default='')
    stb_android = models.IntegerField(default=12)
    country = models.CharField(max_length=200, default='')
    natco_node = models.CharField(max_length=20, default='')


# class TestIteration(TimeStampedModel):

#     release = models.ForeignKey(STBSRelease, on_delete=models.CASCADE)
#     script = models.ForeignKey('testcase_app.TestCaseModel', on_delete=models.CASCADE)
#     iteration_numbers = models.IntegerField()
#     load_times = models.CharField(max_length=200)
#     cpu_usage = models.CharField(max_length=200)
#     ram_usage = models.CharField(max_length=200)


# class PercentileReport(TimeStampedModel):
#     release = models.ForeignKey(STBSRelease, on_delete=models.CASCADE)
#     script = models.ForeignKey('testcase_app.TestCaseModel', on_delete=models.CASCADE)
#     load_time = models.CharField(max_length=200)
#     cpu_usage = models.CharField(max_length=200)
#     ram_usage = models.CharField(max_length=200)
