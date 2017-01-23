from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Category, Product

# Create your views here.


class CategoryListView(ListView):
    template_name = "categories_list.html"
    context_object_name = "categories_list"
    model = Category


class CategoryView(ListView):
    template_name = "products_list.html"
    model = Product
    context_object_name = "products_list"

    def get(self, request, *args, **kwargs):
        self.cat_id = kwargs['cat_id']
        return super(CategoryView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super(CategoryView, self).get_context_data(*args, **kwargs)
        category = Category.objects.get(pk=self.cat_id)
        ctx["category"] = category
        ctx["products_list"] = Product.objects.filter(category=category)
        return ctx

    def get_queryset(self):
        return Product.objects.filter(category__id=self.cat_id)


class ProductsListView(ListView):
    template_name = "products_list.html"
    queryset = Product.objects.order_by("name").all()
    context_object_name = "products_list"


class ProductView(DetailView):
    template_name = "product.html"
    model = Product
    context_object_name = "product"
