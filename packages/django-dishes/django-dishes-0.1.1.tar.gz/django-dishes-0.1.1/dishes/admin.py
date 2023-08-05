from django.contrib import admin
from dishes.models import * 

admin.site.register(Category)
admin.site.register(Menu)
admin.site.register(Ingredient)
admin.site.register(IngredientAmount)
admin.site.register(Recipe)
admin.site.register(Delivery)
admin.site.register(Dish)
