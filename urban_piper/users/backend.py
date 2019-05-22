from django.conf import settings
from django.contrib.auth.backends import ModelBackend

# class AuthenticationBackend(ModelBackend):

#     def authenticate(self, *args, **kwargs):
#         return self.auth_user_type(super().authenticate(*args, **kwargs))
        
#     def get_user(self, *args, **kwargs):
#         return self.auth_user_type(super().get_user(*args, **kwargs))

#     def auth_user_type(self, user):
#         try:
#             sm_user = StorageManager.objects.get(pk=user.pk)
#             return sm_user
#         except:
#             return None

#         try:
#             dp_user = DeliveryPerson.objects.get(pk=user.pk)
#             return dp_user
#         except:
#             return None

#         return user