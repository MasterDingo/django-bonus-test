from django.contrib import admin

from .models import Category, Product, Bonus

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ("name",)


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ("name",)


class BonusAdmin(admin.ModelAdmin):
    model = Bonus
    list_filter = ("user", "start_date", "end_date")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Bonus, BonusAdmin)
