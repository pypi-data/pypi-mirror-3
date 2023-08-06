from django.db import models

from linaro_django_xmlrpc.models import ExposedAPI


class PermissionsModel(models.Model):
    class Meta:
        permissions = (
            ('can_view_raw_data', "Can view raw data"),
        )

class LinaroGraphicsAPI(ExposedAPI):

    def demoMethod(self):
        """
        This is a demo method.
        """
        return 42
