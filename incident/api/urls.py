from rest_framework import routers

from incident.api import views


router = routers.DefaultRouter()
router.register(r'incidents', views.IncidentViewSet, basename='incidentpage')
router.register(r'journalists', views.JournalistViewSet)
router.register(r'institutions', views.InstitutionViewSet)

api_urls = router.urls
