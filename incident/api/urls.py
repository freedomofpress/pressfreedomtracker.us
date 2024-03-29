from django.urls import re_path, include
from rest_framework import routers

from incident.api import views


router = routers.DefaultRouter()
router.register(r'incidents', views.IncidentViewSet, basename='incidentpage')
router.register(r'journalists', views.JournalistViewSet)
router.register(r'institutions', views.InstitutionViewSet)
router.register(r'governmentworkers', views.GovernmentWorkerViewSet)
router.register(r'charges', views.ChargeViewSet)
router.register(r'nationalities', views.NationalityViewSet)
router.register(r'politicians', views.PoliticianOrPublicViewSet)
router.register(r'venues', views.VenueViewSet)
router.register(r'equipment', views.EquipmentViewSet)
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    re_path(
        r'^api/(?P<version>(edge))/',
        include(router.urls),
    ),
]
