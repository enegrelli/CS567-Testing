import pytest
from fractions import Fraction
from list import adjust_recipe, adjust_quantity

# Test adjusting recipe
def test_adjust_recipe():
    sample_recipe = {
        "2 Meat Meatloaf": {
            "Description": ['Dinner', 'American', 'High-Protien', 'Easy', 'Beef', 'Comfort'],
            "Directions": [
                "Preheat oven to 350F.",
                "Soften the bread crumbs in the milk for a few minutes, then pour off the excess milk.",
                "Combine the 2 meats and mix well. Add all other ingredients and mix until thoroughly combined.",
                "Place in large loaf pan, 2 smaller loaf pans or shape into loaf shape and bake on flat baking pan.",
                "Bake for 1 hour at 350 or until browned and fully cooked inside."
            ],
            "Ingredients": {
                "Bread crumbs": "1/2 cup, $1",
                "Carrot": "1 shredded, $0.90",
                "Dijon mustard": "1 teaspoon, $1.30",
                "Dried Thyme": "1/2 teaspoon, $1.70",
                "Eggs": "2, $1.70",
                "Garlic cloves": "2 minced, $0.80",
                "Ground beef": "1 1/2 pound, $7",
                "Ground pork": "1/2 pound, $1.50",
                "Onion": "1 chopped finely, $0.70",
                "Pepper": "1/2 teaspoon, $4",
                "Salt": "1 teaspoon, $2"
            },
            "Rating": 3,
            "Serving Size": {
                "Calories per serving": 350,
                "People served": 4
            }
        }
    }

    desired_serving_size = 6
    adjusted_recipe = adjust_recipe(sample_recipe["2 Meat Meatloaf"], desired_serving_size)

    assert len(adjusted_recipe["Ingredients"]) == len(sample_recipe["2 Meat Meatloaf"]["Ingredients"])

    # Check if the serving size has been adjusted correctly
    assert adjusted_recipe["Serving Size"]["People served"] == desired_serving_size

    # Check if the ingredients quantities and costs have been adjusted correctly
    expected_adjusted_ingredients = {
        "Bread crumbs": "3/4 cup, $1.50",
        "Carrot": "1 1/2 shredded, $1.35",
        "Dijon mustard": "1 1/2 teaspoon, $1.95",
        "Dried Thyme": "3/4 teaspoon, $2.55",
        "Eggs": "3, $2.55",
        "Garlic cloves": "3 minced, $1.20",
        "Ground beef": "2 1/4 pound, $10.50",
        "Ground pork": "3/4 pound, $2.25",
        "Onion": "1 1/2 chopped finely, $1.05",
        "Pepper": "3/4 teaspoon, $6.00",
        "Salt": "1 1/2 teaspoon, $3.00"
    }

    for ingredient, details in adjusted_recipe["Ingredients"].items():
        assert details == expected_adjusted_ingredients[ingredient]

# Test adjusting quantity
def test_adjust_quantity():
    assert adjust_quantity("1 teaspoon", 0.5) == "1/2 teaspoon"
    assert adjust_quantity("2", 1.5) == "3"

# Run the tests
if __name__ == "__main__":
    pytest.main()
