from companies.views.base import Base
from companies.utils.permissions import EmployeesPermission, GroupPermission
from companies.models import Employee, Enterprise
from companies.serializers import EmployeesSerializer, EmployeeSerializer

from accounts.auth import Authentication
from accounts.models import User_Group, User

from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException


class Employees(Base):
    permission_classes = [EmployeesPermission]

    def get_enterprise_id(self, user_id):
        try:
            # Assuming you have a relationship between users and enterprises
            enterprise = Enterprise.objects.get(user_id=user_id)
            return enterprise.id
        except Enterprise.DoesNotExist:
            raise APIException('Enterprise not found for the given user.')
        
    def get(self, request):
        enterprise_id = self.get_enterprise_id(request.user.id)
        owner_id = Enterprise.objects.values('user_id').filter(id=enterprise_id).first()['user_id']
        employees = Employee.objects.filter(enterprise_id=enterprise_id).exclude(user_id=owner_id).all()
        serializer = EmployeesSerializer(employees, many=True)

        return Response({'employees': serializer.data})

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')

        if not all([name, email, password]):
            return Response(
                {"error": "Nome, email e senha são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        enterprise_id = self.get_enterprise_id(request.user.id)

        try:
            signup_user = Authentication().signup(
                name=name,
                email=email,
                password=password,
                type_account='employee',
                company_id=enterprise_id
            )
            if isinstance(signup_user, User):
                return Response({'success': True}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': signup_user['error']}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EmployeeDetail(Base):
    permission_classes = [EmployeesPermission]

    def get(self, request, employee_id):
        employee = self.get_employee(employee_id, request.user.id)
        serializer = EmployeeSerializer(employee)

        return Response({'employee': serializer.data})
    
    def put(self, request, employee_id):
        groups = request.data.get('groups')

        employee = self.get_employee(employee_id, request.user.id)

        name = request.data.get('name') or employee.user.name
        email = request.data.get('email') or employee.user.email

        if email != employee.user.email and User.objects.filter(email=email).exists():
            raise APIException('Email já cadastrado', code='email_already_use')
         
        User.objects.filter(id=employee.user.id).update(
            name=name, 
            email=email
            )
        User_Group.objects.filter(user_id=employee.user.id).delete()

        if groups:
            groups = groups.split(',')

            for group in groups:
                self.get_group(group, employee.enterprise_id)
                User_Group.objects.create(
                    group_id=group_id, 
                    user_id=employee.user.id
                )
        return Response({'sucess': True})

    def delete(self, request, employee_id):
        employee = self.get_employee(employee_id, request.user.id)
        check_if_owner = User.objects.filter(id=employee.user.id, is_owner=1).exists()

        if check_if_owner:
            raise APIException('Não é possível demitir o dono da empresa')

        employee.delete()
        User.objects.filter(id=employee.user.id).delete()

        return Response({'sucess': True})