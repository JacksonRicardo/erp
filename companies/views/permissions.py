from companies.views.base import Base
from companies.utils.permissions import GroupPermission
from companies.serializers import PermissionsSerializer

from rest_framework.response import Response

from django.contrib.auth.models import Permission

class PermissionDetail(Base):
    permission_classes = [GroupPermission]

    def get(self, request, permission_id):
        permissions = Permission.objects.filter(content_type_id__in=[2, 7, 11, 13]).all()
        serializer = PermissionsSerializer(permissions, many=True)

        return Response({'permissions': serializer.data})