from django.contrib import admin
from .models import (
    HeroSection, GalleryImage, HomepageSection, WebsiteSettings,
    ContactInformation, FAQ, Testimonial,
)

admin.site.register(HeroSection)
admin.site.register(GalleryImage)
admin.site.register(HomepageSection)
admin.site.register(WebsiteSettings)
admin.site.register(ContactInformation)
admin.site.register(FAQ)
admin.site.register(Testimonial)
