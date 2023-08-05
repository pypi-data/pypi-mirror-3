from django.db import models
from django.utils.translation import ugettext_lazy as _

class XauthAssociation(models.Model):
    created = models.DateTimeField(_("Creation date"), auto_now_add=True)
    service = models.CharField(_("Service name"), max_length=50)
    identity = models.CharField(_("Identity"), max_length=255, unique=True)
    user = models.ForeignKey("auth.User", verbose_name=_("User"))

    class Meta:
        verbose_name = _("Association")
        verbose_name_plural = _("Associations")
