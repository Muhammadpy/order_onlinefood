from django.contrib import admin
from .models import Category
from .models import FoodItem


admin.site.register(Category)
admin.site.register( FoodItem)

