from accounts.views.base import Base
from accounts.models import User
from rest_framework.permissions import IsAuthenticated
from accounts.serializers import UserSerializer
from rest_framework.response import Response

from rest_framework.exceptions import NotFound

class GetUser(Base):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            raise NotFound("User not found.")

        enterprise = self.get_enterprise_user(user)

        serializer = UserSerializer(user)

        return Response({  
            'user': serializer.data,
            'enterprise': enterprise
        })


        