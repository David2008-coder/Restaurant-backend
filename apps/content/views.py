from rest_framework import viewsets, generics
from apps.common.permissions import IsAdminOrReadOnly
from .models import (
    HeroSection, GalleryImage, HomepageSection, WebsiteSettings,
    ContactInformation, FAQ, Testimonial,
)
from .serializers import (
    HeroSectionSerializer, GalleryImageSerializer, HomepageSectionSerializer,
    WebsiteSettingsSerializer, ContactInformationSerializer, FAQSerializer, TestimonialSerializer,
)


class HeroSectionViewSet(viewsets.ModelViewSet):
    queryset = HeroSection.objects.all()
    serializer_class = HeroSectionSerializer
    permission_classes = [IsAdminOrReadOnly]


class ActiveHeroView(generics.RetrieveAPIView):
    """Convenience endpoint: GET the single hero the public homepage should render."""
    serializer_class = HeroSectionSerializer

    def get_object(self):
        return HeroSection.objects.filter(is_active=True).first()


class GalleryImageViewSet(viewsets.ModelViewSet):
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAdminOrReadOnly]
    ordering_fields = ["display_order", "created_at"]

    def get_queryset(self):
        qs = GalleryImage.objects.all()
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(is_hidden=False)
        return qs


class HomepageSectionViewSet(viewsets.ModelViewSet):
    queryset = HomepageSection.objects.all()
    serializer_class = HomepageSectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "key"


class WebsiteSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = WebsiteSettingsSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self):
        obj, _ = WebsiteSettings.objects.get_or_create(pk=1)
        return obj


class ContactInformationView(generics.RetrieveUpdateAPIView):
    serializer_class = ContactInformationSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self):
        obj, _ = ContactInformation.objects.get_or_create(pk=1)
        return obj


class FAQViewSet(viewsets.ModelViewSet):
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = FAQ.objects.all()
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            qs = qs.filter(is_active=True)
        return qs


class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminOrReadOnly]
