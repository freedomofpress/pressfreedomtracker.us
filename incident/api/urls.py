from rest_framework import routers

from incident.api.views import IncidentViewSet


router = routers.DefaultRouter()
router.register(r'incidents', IncidentViewSet, basename='incidentpage')

api_urls = router.urls
