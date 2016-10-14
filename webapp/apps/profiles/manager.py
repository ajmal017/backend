#-*- coding: utf-8 -*-

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.utils.crypto import get_random_string


class CustomUserManager(UserManager):
    """
     This class is necessary to create if using custom user model is desired
    """

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """

        email = self.normalize_email(email)
        temp_phone ='0000000000'
        extra_fields['username'] = extra_fields['username'] if extra_fields.get('username') else email
        extra_fields['phone_number'] = extra_fields['phone_number'] if extra_fields.get('phone_number') else temp_phone
        user = self.model(email=email, is_staff=is_staff, is_active=True, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: creates a super user
        """
        u = self.create_user(kwargs['email'], password=kwargs['password'])
        u.username = kwargs['email']
        u.is_staff = True
        u.save(using=self._db)
        return u

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_unconfirmed_user(self, email=None, password=None, account_type=None, **extra_fields):
        """
        :rtype: profiles.models.User
        """
        if password is None:
            password = make_password(None)
        return super(CustomUserManager, self).create_user(
            email, password, account_type=account_type,
            is_active=False, **extra_fields
        )

    def generate_random_username(self):
        """
        Usernames that start with '!' are generated randomly and
        cannot be used for login until changed by the user.
        """
        return "!{}".format(get_random_string(length=16))
