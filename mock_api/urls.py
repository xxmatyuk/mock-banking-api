from django.contrib import admin
from django.urls import path, include

from rest_framework import routers, permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from account.views import BankingAccountsViewSet, CustomersViewSet, TransactionsViewSet

router = routers.SimpleRouter()
router.register(r'accounts', BankingAccountsViewSet, basename='accounts')
router.register(r'customers', CustomersViewSet, basename='customers')
router.register(r'transactions', TransactionsViewSet, basename='transactions')

urlpatterns = [
    # API urls
    path('', include(router.urls)),
    # Admin site
    path('admin/', admin.site.urls),
    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui')
]
