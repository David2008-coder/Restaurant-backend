from rest_framework import viewsets, permissions
from apps.common.utils import log_activity
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "reviews"

    def get_queryset(self):
        qs = Review.objects.all()
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(status=Review.Status.APPROVED)
        return qs

    def perform_update(self, serializer):
        instance = serializer.save()
        log_activity(self.request.user, f"set review status to {instance.status}", instance)
