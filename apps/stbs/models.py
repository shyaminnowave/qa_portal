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
    manufacture = models.ManyToManyField(STBManufacture, blank=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s' % self.country

    class Meta:
        permissions = [
            ("view_natco_option", "Can View natco Option List")
        ]


class NactoManufactureLanguage(TimeStampedModel):
    natco = models.ForeignKey(Natco, on_delete=models.CASCADE, related_name='natco_info')
    device_name = models.ForeignKey(STBManufacture, on_delete=models.CASCADE, related_name='natco_manufacture')
    language_name = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='natco_language')
    history = HistoricalRecords()

    def __str__(self) -> str:
        return '%s - %s' % (self.natco.natco, self.language_name.language_name)

    class Meta:
        permissions = [
            ("view_natco_manufacture_option", "Can View Natco Manufacture Language Option List")
        ]


class STBNode(TimeStampedModel):
    node_id = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.node_id


class STBNactoVersions(TimeStampedModel):

    natco = models.ForeignKey(Natco, on_delete=models.CASCADE)
    version = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.natco.natco} - {self.version}"


class STBRelease(TimeStampedModel):

    stb_node = models.ForeignKey(STBNode, on_delete=models.CASCADE)
    natco = models.ForeignKey(Natco, on_delete=models.CASCADE, max_length=255, default='')
    stb_build_info = models.CharField(max_length=255, default='')
    stb_release = models.CharField(max_length=255, default='')
    stb_firmware = models.CharField(max_length=255, default='')
    stb_android = models.IntegerField(default=12)

    def __str__(self):
        return f"{self.natco.natco} {self.stb_release} {self.stb_android} - {self.stb_node.node_id[-3]}"


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
