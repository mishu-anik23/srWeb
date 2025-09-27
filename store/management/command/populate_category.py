from django.core.management.base import BaseCommand
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
            "Vegetables": None,  # Will be a main category with no subcategories
            "Homemade Snacks": [
                "Sweets Variant",
                "Spicy Snacks"
            ]
        }

        # Clear existing categories
        Category.objects.all().delete()

        # Create categories
        for main_cat_name, sub_data in categories_data.items():
            main_category, created = Category.objects.get_or_create(
                name=main_cat_name,
                slug=main_cat_name.lower().replace(' ', '-')
            )

            if sub_data is not None:
                if isinstance(sub_data, dict):  # Has subcategories
                    for sub_cat_name, product_types in sub_data.items():
                        sub_category, created = Category.objects.get_or_create(
                            name=sub_cat_name,
                            slug=sub_cat_name.lower().replace(' ', '-'),
                            parent=main_category
                        )

                        for product_type_name in product_types:
                            Category.objects.get_or_create(
                                name=product_type_name,
                                slug=product_type_name.lower().replace(' ', '-'),
                                parent=sub_category
                            )

                elif isinstance(sub_data, list):  # Direct product types under main category
                    for product_type_name in sub_data:
                        Category.objects.get_or_create(
                            name=product_type_name,
                            slug=product_type_name.lower().replace(' ', '-'),
                            parent=main_category
                        )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated categories!')
        )