from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie import fields
from dishes.models import Menu, Dish

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        allowed_methods = ['get']

class DishResource(ModelResource):

    class Meta:
        queryset = Dish.objects.all()
        resource_name = 'dish'
        authorization= Authorization()

class MenuResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'created_by')

    class Meta:
        queryset = Menu.active_objects.all()
        resource_name = 'menu'
        authorization= Authorization()

