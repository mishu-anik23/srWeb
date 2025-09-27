from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category


class Command(BaseCommand):
    help = 'Populate categories for Sunrise Supermarkt'

    def handle(self, *args, **kwargs):
        # Define your category structure
        categories_data = {
            "Indian": {
                "Rice & Flour": [
                    "Basmati Rice",
                    "South Indian Rice",
                    "Poha, Mamra & Vermicelli",
                    "Chapati Atta (Indian Flour)",
                    "Flour Varieties"
                ],
                "Lentils & Spices": [
                    "Lentils",
                    "Powdered Spices",
                    "Whole Spices",
                    "Mixed Spices"
                ],
                "Snacks & Sweets": [
                    "Snacks",
                    "Biscuits, Cookies and Cake Rusks",
                    "Sweets",
                    "Tea & Coffee"
                ],
                "Condiments": [
                    "Pickles",
                    "Chutneys",
                    "Sauces & Pastes - Indian",
                    "Mango Pulp",
                    "Juice"
                ],
                "Essentials": [
                    "Paneer & Milk Products",
                    "Ghee & Oils",
                    "Tamarind",
                    "Papad",
                    "Coconut Products",
                    "Jaggery Products"
                ],
                "Ready to Eat": [
                    "Instant Mixes",
                    "Ready to Eat",
                    "Rotis and Naan",
                    "Instant Noodles - Indian",
                    "Canned Vegetables, Fish & Meat"
                ],
                "Personal & Home Care": [
                    "Personal Care & Nutrition",
                    "Home Care"
                ]
            },
            "Asian": {
                "Sauces & Pastes": [
                    "Soy Sauce",
                    "Chilli Sauces - Sriracha & More",
                    "Ready Curry & Pastes",
                    "Sauces & Pastes - Asian",
                    "Vinegar"
                ],
                "Noodles & Soups": [
                    "Instant Noodles - Asian",
                    "Rice Noodles & Vermicelli (Glass Noodles)"
                ],
                "Rice & Flour": [
                    "Jasmine, Sticky & Sushi Rice",
                    "Rice Paper",
                    "Flour & Flour Products"
                ],
                "Spices & Seasonings": [
                    "Greeny Leaves",
                    "Spice Mixes in Oil",
                    "Spices paste"
                ],
                "Essentials": [
                    "Cooking Oils",
                    "Peanut Butter"
                ],
                "Snacks & Sweets": [
                    "Snacks, Chips & Crackers"
                ]
            },
            "Frozen": [
                "Bangladeshi Snacks",
                "Indian Snacks",
                "Roti/Parathas/Naan",
                "Asian Snacks",
                "Fish & Meat",
                "Vegetables"
            ],
            "Vegetables": None,
            "Homemade Snacks": [
                "Sweets Variant",
                "Spicy Snacks"
            ]
        }

        # Clear existing categories
        Category.objects.all().delete()
        self.stdout.write("Cleared existing categories...")

        # Helper function to create unique slugs
        def get_unique_slug(base_slug, parent=None):
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            return slug

        # Create categories
        for main_cat_name, sub_data in categories_data.items():
            main_slug = slugify(main_cat_name)
            main_slug = get_unique_slug(main_slug)

            main_category, created = Category.objects.get_or_create(
                name=main_cat_name,
                defaults={'slug': main_slug}
            )

            self.stdout.write(f"Created main category: {main_cat_name}")

            if sub_data is not None:
                if isinstance(sub_data, dict):  # Has subcategories
                    for sub_cat_name, product_types in sub_data.items():
                        sub_slug = slugify(sub_cat_name)
                        sub_slug = get_unique_slug(sub_slug, main_category)

                        sub_category, created = Category.objects.get_or_create(
                            name=sub_cat_name,
                            parent=main_category,
                            defaults={'slug': sub_slug}
                        )

                        self.stdout.write(f"  └── Created subcategory: {sub_cat_name}")

                        for product_type_name in product_types:
                            type_slug = slugify(product_type_name)
                            type_slug = get_unique_slug(type_slug, sub_category)

                            Category.objects.get_or_create(
                                name=product_type_name,
                                parent=sub_category,
                                defaults={'slug': type_slug}
                            )

                            self.stdout.write(f"      └── Created product type: {product_type_name}")

                elif isinstance(sub_data, list):  # Direct product types under main category
                    for product_type_name in sub_data:
                        type_slug = slugify(product_type_name)
                        type_slug = get_unique_slug(type_slug, main_category)

                        Category.objects.get_or_create(
                            name=product_type_name,
                            parent=main_category,
                            defaults={'slug': type_slug}
                        )

                        self.stdout.write(f"  └── Created product type: {product_type_name}")

        # Display the category tree
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Category Tree Created:")
        self.stdout.write("=" * 50)

        root_categories = Category.objects.filter(level=0)
        for category in root_categories:
            self.stdout.write(f"• {category.name}")
            for child in category.get_children():
                self.stdout.write(f"  └── {child.name}")
                for grandchild in child.get_children():
                    self.stdout.write(f"      └── {grandchild.name}")

        self.stdout.write(
            self.style.SUCCESS('\nSuccessfully populated categories!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total categories created: {Category.objects.count()}')
        )