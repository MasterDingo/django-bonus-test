from django.conf.urls import url
from django.contrib.auth.views import (
     login as login_view, logout as logout_view
)
from .views import (
     CategoryListView, CategoryView, ProductsListView, ProductView
)

urlpatterns = [
    url(r'login', login_view, {"template_name": "login.html"}, name="login"),
    url(r'logout', logout_view, {"next_page": "/"}, name="logout"),
    url(r'^$', CategoryListView.as_view(), name="categories_list"),
    url(r'category/(?P<cat_id>\d+)', CategoryView.as_view(), name="category"),
    url(r'products', ProductsListView.as_view(),
        name="products_list"),
    url(r'product/(?P<pk>\d+)', ProductView.as_view(), name="product"),
]
