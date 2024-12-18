from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from accounts.models import User_Group, GroupPermission
from companies.models import Enterprise, Employee

class Base(APIView):
    def get_enterprise_user(self, user_id):
        enterprise ={
            'is_owner': False,
            'permissions': []
        }

        enterprise['is_owner']  = Enterprise.objects.filter(user_id=user_id).exists()

        if enterprise['is_owner']: return enterprise

        employee = Employee.objects.filter(user_id=user_id).first()

        if not employee: 
            raise APIException('Este usuário não um funcionário')

        groups = user_Groups.objects.filter(user_id=user_id).all()

        for g in groups:
            group = g.groups
            
            permissions = Group_Permissions.objects.filter(group_id=group_id).all()

            for p in permissions:
                enterprise['permissions'].append({
                    'id': p.permission_id,
                    'label': p.permission.name,
                    'codename': p.permission.codename
                })
        return enterprise