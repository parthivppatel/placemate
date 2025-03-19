from django.db import models
from .roles import Role
from .permissions import Permission

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Role_Permission'
        unique_together = ('role', 'permission')
