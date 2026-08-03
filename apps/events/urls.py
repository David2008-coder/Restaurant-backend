from rest_framework.routers import DefaultRouter
from .views import EventViewSet, BookingViewSet

router = DefaultRouter()
router.register("events", EventViewSet, basename="event")
router.register("bookings", BookingViewSet, basename="booking")

urlpatterns = router.urls
