from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    HeroSectionViewSet, ActiveHeroView, GalleryImageViewSet, HomepageSectionViewSet,
    WebsiteSettingsView, ContactInformationView, FAQViewSet, TestimonialViewSet,
)

router = DefaultRouter()
router.register("hero", HeroSectionViewSet, basename="hero")
router.register("gallery", GalleryImageViewSet, basename="gallery")
router.register("homepage-sections", HomepageSectionViewSet, basename="homepage-section")
router.register("faqs", FAQViewSet, basename="faq")
router.register("testimonials", TestimonialViewSet, basename="testimonial")

urlpatterns = [
    path("hero/active/", ActiveHeroView.as_view(), name="hero-active"),
    path("settings/", WebsiteSettingsView.as_view(), name="website-settings"),
    path("contact/", ContactInformationView.as_view(), name="contact-info"),
] + router.urls
