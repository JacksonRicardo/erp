from rest_framework.exceptions import AuthenticationFailed, APIException
from django.contrib.auth.hashers import check_password, make_password
from accounts.models import User
from companies.models import Enterprise, Employee

class Authentication:
    def signin(self, email=None, password=None) -> User:
        """
        Autentica um usuário com email e senha.
        """
        exception_auth = AuthenticationFailed('Email e/ou senha incorreto(s)')

        # Verifica se o usuário existe
        user_exists = User.objects.filter(email=email).exists()
        if not user_exists:
            raise exception_auth

        # Busca o usuário
        user = User.objects.filter(email=email).first()

        # Verifica a senha
        if not check_password(password, user.password):
            raise exception_auth

        return user

    def signup(self, name, email, password, type_account='owner', company_id=None):
        """
        Cria um novo usuário e associa a uma empresa (se necessário).

        Args:
            name (str): Nome do usuário.
            email (str): Email do usuário.
            password (str): Senha do usuário.
            type_account (str): Tipo de conta ('owner' ou 'employee').
            company_id (int): ID da empresa (necessário para tipo 'employee').

        Returns:
            User: Retorna o objeto User em caso de sucesso.
            dict: Retorna um erro em caso de falha.
        """
        if not name or name == '':
            raise APIException('O nome não deve ser null')

        if not email or email == '':
            raise APIException('O email não deve ser null')

        if not password or password == '':
            raise APIException('O password não deve ser null')

        if type_account == 'employee' and not company_id:
            raise APIException('O ID da empresa não deve ser null para funcionários')

        # Verifica se o email já está em uso
        if User.objects.filter(email=email).exists():
            raise APIException('Esse email já existe na plataforma')

        # Criptografa a senha
        password_hashed = make_password(password)
        print(password_hashed)
        print(name, email, password_hashed, type_account, company_id)
        # Cria o usuário
        created_user = User.objects.create(
            name=name,
            username=email,
            email=email,
            password=password_hashed,
            is_owner=0 if type_account == 'employee' else 1
        )

        # Criação de uma empresa se o tipo for 'owner'
        if type_account == 'owner':
            created_enterprise = Enterprise.objects.create(
                name=f'Empresa de {name}',  # Você pode personalizar o nome da empresa
                user_id=created_user.id
            )
            # Se for proprietário, associamos a empresa ao usuário

        # Criação de um funcionário (employee) e associação à empresa
        if type_account == 'employee':
            if not company_id:  # Se não for fornecido, associa à empresa do dono
                raise APIException('Empresa não encontrada para o funcionário')

            Employee.objects.create(
                enterprise_id=company_id,
                user_id=created_user.id
            )

        return created_user  # Retorna o usuário criado