"""
Seeds the database with Itagokwaife Grillspot's real content — categories,
products, hero, gallery and settings — using the restaurant's own photos.

This is what the spec means by "never hardcode": the React frontend renders
nothing here directly. It only ever calls the API. This command is simply
how those real photos and menu items get into the database the API reads from.

Run with:  python manage.py seed_restaurant
"""
from django.core.management.base import BaseCommand
from django.core.files import File
from pathlib import Path

from apps.catalog.models import Category, Product
from apps.content.models import HeroSection, GalleryImage, WebsiteSettings, ContactInformation, HomepageSection

SEED_DIR = Path(__file__).resolve().parents[4] / "media" / "seed"


def img(name):
    path = SEED_DIR / name
    return File(open(path, "rb"), name=name)


class Command(BaseCommand):
    help = "Seed categories, products, hero and gallery with the restaurant's real photos."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Itagokwaife Grillspot...")

        # ---------------- Website settings & contact ----------------
        settings_obj, _ = WebsiteSettings.objects.get_or_create(pk=1)
        settings_obj.site_name = "Itagokwaife Grillspot"
        settings_obj.tagline = "Grilled over real fire."
        settings_obj.logo.save("logo-red-circle.png", img("logo-red-circle.png"), save=False)
        settings_obj.save()

        contact, _ = ContactInformation.objects.get_or_create(pk=1)
        contact.address = "Itagokwaife Grillspot, Lagos, Nigeria"
        contact.whatsapp_number = "+2340000000000"
        contact.opening_hours = {"mon_thu": "11:00 - 23:00", "fri_sun": "11:00 - 00:00"}
        contact.save()

        # ---------------- Hero ----------------
        hero, _ = HeroSection.objects.get_or_create(heading="Grilled over real fire.")
        hero.subtitle = (
            "Whole fish, turkey and chicken, seasoned heavy and smoked slow over open coals — "
            "foil-wrapped, char-kissed, and served the way Lagos likes it."
        )
        hero.image.save("grilled-chicken.png", img("grilled-chicken.png"), save=False)
        hero.button_text = "See the Menu"
        hero.button_link = "/menu"
        hero.is_active = True
        hero.save()

        story, _ = HomepageSection.objects.update_or_create(
            key="our-story",
            defaults=dict(
                title="Built on the grill, not the menu board.",
                body=(
                    "Itagokwaife started as a street-side grill in Lagos — one man, one rack of coals, "
                    "and a promise to never rush the fire. Every fish is scaled and marinated by hand, "
                    "every piece of chicken and turkey rests over the flame until the skin blisters, and "
                    "everything leaves the grill wrapped hot in foil with pepper, onion and fresh veg."
                ),
                display_order=1,
                is_active=True,
            ),
        )
        story.image.save("chef-at-grill.png", img("chef-at-grill.png"), save=False)
        story.save()

        # ---------------- Categories ----------------
        categories = {
            "Grilled Fish": "Whole fish, scaled and smoked over open coals.",
            "Grilled Chicken": "Char-marked chicken quarters, deeply seasoned.",
            "Grilled Turkey": "Smoky, tender turkey off the grill.",
            "Shawarma": "Rolled fresh, extra creamy, 100% organic fillings.",
            "BBQ & Peppered Meat": "Peppersteak style, sealed in foil with fries.",
            "Small Chops & Extras": "Sides, fries and small chops.",
            "Drinks & Wine": "Soft drinks and a curated wine selection.",
        }
        cat_objs = {}
        for i, (name, desc) in enumerate(categories.items()):
            cat, _ = Category.objects.get_or_create(name=name, defaults={"description": desc, "display_order": i})
            cat_objs[name] = cat

        # ---------------- Products (built from the restaurant's real photos) ----------------
        products = [
            dict(
                name="Whole Grilled Fish", category="Grilled Fish",
                short_description="Scaled, butterflied and smoked whole until the skin cracks.",
                description="Our signature whole fish — hand-scaled, marinated in-house pepper blend, and smoked "
                             "whole over open coals until the skin chars and cracks. Served hot off the grill.",
                price=8500, image="whole-fish-grill.png", spicy_level=3, is_featured=True, tags="fish,signature,grilled",
            ),
            dict(
                name="Grilled Chicken Quarters", category="Grilled Chicken",
                short_description="Char-marked, deeply seasoned, off the bone tender.",
                description="Chicken quarters marinated overnight and grilled low and slow over open flame for "
                             "deep char and tender meat that pulls straight off the bone.",
                price=6000, image="grilled-chicken.png", spicy_level=2, is_featured=True, tags="chicken,grilled,bestseller",
            ),
            dict(
                name="Itagokwaife Shawarma", category="Shawarma",
                short_description="100% organic fillings, extra creamy sauce, rolled fresh.",
                description="Our take on the Lagos classic — shredded chicken, fresh vegetables and a signature "
                             "creamy sauce, rolled fresh to order in warm flatbread.",
                price=3000, image="shawarma-poster.png", spicy_level=1, is_featured=True, tags="shawarma,wrap,fan-favorite",
            ),
            dict(
                name="Foil-Wrapped Peppered Fish & Fries", category="BBQ & Peppered Meat",
                short_description="Sealed in foil with pepper, onion and crisp fries.",
                description="Whole fish rubbed in our peppersteak blend, sealed in foil with onions and fresh "
                             "pepper, and served with a side of hand-cut fries.",
                price=9000, image="foil-fish-tray.png", spicy_level=4, tags="fish,peppered,foil",
            ),
            dict(
                name="Fish & Fries Platter", category="Grilled Fish",
                short_description="Char-grilled fish, hand-cut fries, fresh peppers.",
                description="A full plate — char-grilled fish with hand-cut fries and fresh pepper and vegetable "
                             "garnish, straight off the coals.",
                price=7500, image="fish-fries-closeup.png", spicy_level=2, tags="fish,platter",
            ),
            dict(
                name="Fish & Garden Salad", category="Grilled Fish",
                short_description="Smoked fish over cucumber, tomato, onion and greens.",
                description="Smoked fish plated over a fresh garden salad — cucumber, tomato, onion and crisp "
                             "greens — for a lighter option off the same grill.",
                price=7000, image="fish-salad-foil.png", spicy_level=1, tags="fish,salad,light",
            ),
        ]

        for p in products:
            cat = cat_objs[p["category"]]
            product, created = Product.objects.get_or_create(
                name=p["name"],
                defaults=dict(
                    category=cat,
                    short_description=p["short_description"],
                    description=p["description"],
                    price=p["price"],
                    spicy_level=p["spicy_level"],
                    is_featured=p.get("is_featured", False),
                    tags=p["tags"],
                ),
            )
            if created:
                product.main_image.save(p["image"], img(p["image"]), save=True)

        # ---------------- Gallery ----------------
        gallery_images = [
            ("night-outdoor-seating.png", "Guests on the patio under the itagokwaife sign"),
            ("storefront.png", "The itagokwaife storefront"),
            ("chef-at-grill.png", "Our grillmaster wrapping fish in foil"),
            ("fish-salad-foil.png", "Grilled fish plated with fresh salad"),
            ("whole-fish-grill.png", "Whole fish grilling side by side"),
            ("grilled-chicken.png", "Rows of grilled chicken on the grate"),
        ]
        for i, (filename, caption) in enumerate(gallery_images):
            if not GalleryImage.objects.filter(caption=caption).exists():
                gallery = GalleryImage(caption=caption, display_order=i)
                gallery.image.save(filename, img(filename), save=True)

        self.stdout.write(self.style.SUCCESS("Seed complete — categories, products, hero and gallery are live."))
