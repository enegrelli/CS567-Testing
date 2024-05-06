from fractions import Fraction
import json
import copy
import logging
import random

# Constants
CURRENCY_SYMBOL = '$'
COST_FORMAT = '{:.2f}'

# Configure logging
logging.basicConfig(level=logging.WARNING)

class FractionEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Fraction):
            return {
                "__fraction__": True,
                "numerator": o.numerator,
                "denominator": o.denominator
            }
        return super().default(o)

def create_shopping_list(recipe_data, desired_serving_size, shopping_list=None):
    if shopping_list is None:
        shopping_list = []
    
    total_cost = 0

    if recipe_data:
        ingredients = recipe_data.get('Ingredients', {})
        adjusted_recipe = adjust_recipe(recipe_data, desired_serving_size)
        cost_total = adjusted_recipe.get('Total Cost', 0)

        for ingredient, ingredient_details in adjusted_recipe['Ingredients'].items():
            converted_amount = ingredient_conversion(ingredient_details)

            if converted_amount is not None:
                cost = float(ingredient_details.split(", ")[-1].split("$")[-1])
                total_cost = cost * converted_amount

                found = False
                for item in shopping_list:
                    if item['ingredient'] == ingredient:
                        item['amount'] += converted_amount
                        item['cost'] += total_cost
                        found = True
                        break

                if not found:
                    shopping_list.append({
                        'ingredient': ingredient,
                        'amount': converted_amount,
                        'cost': total_cost
                    })

    serialized_list = serialize_shopping_list(shopping_list)
    return serialized_list, total_cost


def serialize_shopping_list(shopping_list):
    return json.dumps(shopping_list, cls=FractionEncoder)


def add_to_shopping_list(shopping_list, recipe_data):
    desired_serving_size = 2
    serialized_list, total_cost = create_shopping_list(recipe_data, desired_serving_size, shopping_list)
    return serialized_list, total_cost

def remove_from_shopping_list(shopping_list, recipe_data):
    ingredients_to_remove = recipe_data.get('Ingredients', {}).keys()
    shopping_list[:] = [item for item in shopping_list if item.get('ingredient') not in ingredients_to_remove]



def ingredient_conversion(details):
    conversion = {
        'teaspoon': Fraction(1, 3),
        'clove': Fraction(1, 3),
        'tablespoon': 1,
        'ounce': 2,
        'cup': 16,
        'packet': Fraction(26, 10),
        'pound': 30
    }

    split_details = details.split(', ')
    amount_unit = split_details[0]

    # Check if there's a space - mixed fractions
    if ' ' in amount_unit:
        parts = amount_unit.split(' ')
        if len(parts) == 1:  # whole num
            amount = parts[0]
            unit = split_details[1]
        else:
            amount = ' '.join(parts[:-1])
            unit = parts[-1]

        if unit.lower() in conversion:
            if '/' in amount:
                whole, frac = amount.split(' ')
                frac_num, frac_den = frac.split('/')
                parsed_amount = int(whole) * conversion[unit.lower()] + Fraction(int(frac_num), int(frac_den)) * conversion[unit.lower()]
            else:
                parsed_amount = int(amount) * conversion[unit.lower()]
        else:
            parsed_amount = amount
    else:
        amount = amount_unit
        unit = split_details[1]
        if unit.lower() in conversion:
            parsed_amount = int(amount) * conversion[unit.lower()]
            unit = 'tablespoon'
        else:
            parsed_amount = int(amount)

    return parsed_amount

def float_to_mixed_number(number):
    if isinstance(number, (int, float)):
        # Split the number into the whole part and the fraction
        whole_part = int(number)
        fractional_part = Fraction(number - whole_part).limit_denominator()

        # Check if there is a fraction
        if fractional_part != 0:
            # Format the mixed number as a string
            if whole_part != 0:
                mixed_number = f'{whole_part} {fractional_part.numerator}/{fractional_part.denominator}'
            else:
                mixed_number = f'{fractional_part.numerator}/{fractional_part.denominator}'
            return mixed_number
        else:
            # If there is no fraction, return only the whole part
            return str(whole_part)
    else:
        raise ValueError("Input must be a float or integer")

# Function to calculate total cost from ingredients
def calculate_total_cost(ingredients):
    total_cost = 0
    for cost in ingredients.values():
        # Split the cost into quantity and price parts
        parts = cost.split(', $')
        if len(parts) == 2 and parts[1].replace('.', '', 1).isdigit():
            try:
                # Add the price to the total cost
                total_cost += float(parts[1])
            except ValueError:
                print(f"Error: Invalid cost format '{cost}'")
        else:
            print(f"Error: Invalid cost format '{cost}'")
    return total_cost

def adjust_whole_number(quantity, ratio):
    adjusted_value = int(float(quantity) * ratio)
    return float_to_mixed_number(adjusted_value)

def adjust_fraction(quantity, ratio):
    adjusted_value = Fraction(quantity) * ratio
    return float_to_mixed_number(adjusted_value)

def adjust_mixed_number_with_unit(quantity, ratio, unit):
    whole_part, fraction_part = quantity.split()
    whole_number = int(whole_part)
    fraction = Fraction(fraction_part)
    adjusted_value = (whole_number + fraction) * ratio
    return f"{float_to_mixed_number(adjusted_value)} {unit}"

def adjust_quantity(original_quantity, ratio):
    try:
        # Separate quantity and unit
        parts = original_quantity.split()

        if len(parts) >= 2 and '/' in parts[1]:
            # Handle mixed numbers
            quantity = ' '.join(parts[0:2])  # Join the first two parts (whole and fraction)
            unit = ' '.join(parts[2:]) if len(parts) > 2 else ''
            return adjust_mixed_number_with_unit(quantity, ratio, unit)
        else:
            quantity, unit = parts[0], ' '.join(parts[1:]) if len(parts) > 1 else ''

        if '/' in quantity:
            adjusted_fraction = adjust_fraction(quantity, ratio)
            return f"{adjusted_fraction} {unit}" if unit else adjusted_fraction

        # Try to parse as a fraction
        try:
            fraction_quantity = Fraction(quantity)
            adjusted_value = fraction_quantity * ratio
            return f"{float_to_mixed_number(adjusted_value)} {unit}" if unit else float_to_mixed_number(adjusted_value)
        except ValueError:
            # If parsing as a fraction fails
            adjusted_value = float(quantity) * ratio
            return f"{float_to_mixed_number(adjusted_value)} {unit}" if unit else float_to_mixed_number(adjusted_value)

    except (ValueError, IndexError) as e:
        logging.error(f"Error converting quantity: {original_quantity}. Error: {e}")
        return original_quantity

def adjust_recipe(recipe, desired_servings):
    adjusted_recipe = copy.deepcopy(recipe)

    try:
        if 'Serving Size' in adjusted_recipe:
            adjusted_recipe['Serving Size']['People served'] = desired_servings
        else:
            logging.warning("Warning: 'Serving Size' not found in recipe structure. Serving size not updated.")

        if 'Ingredients' in adjusted_recipe:
            ratio = desired_servings / recipe['Serving Size']['People served']
            # Convert the ingredients dictionary keys to a sorted list
            ingredients = sorted(adjusted_recipe['Ingredients'].keys())
            for ingredient in ingredients:
                details = adjusted_recipe['Ingredients'][ingredient]
                quantity, cost = details.split(', ')
                adjusted_quantity = adjust_quantity(quantity, ratio)
                adjusted_cost = round(float(cost[1:]) * ratio, 2)
                adjusted_recipe['Ingredients'][ingredient] = f"{adjusted_quantity}, {CURRENCY_SYMBOL}{adjusted_cost:.2f}"

            adjusted_recipe['Total Cost'] = sum(float(details.split(', ')[1][1:]) for details in adjusted_recipe['Ingredients'].values())
        else:
            logging.warning("Warning: 'Ingredients' not found in recipe structure. Ingredient quantities and costs not updated.")

        return adjusted_recipe

    except Exception as e:
        logging.error(f"Error adjusting recipe: {e}")
        return recipe

# Sample recipe data
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

# example
desired_serving_size = 6
adjusted_recipe = adjust_recipe(sample_recipe["2 Meat Meatloaf"], desired_serving_size)

print("Before adjusting the recipe:")
for ingredient, details in sample_recipe["2 Meat Meatloaf"]["Ingredients"].items():
    print(details)

print("\n")

print("After adjusting the recipe:")
for ingredient, details in adjusted_recipe["Ingredients"].items():
    print(details)

print("\nExpected output:")
print("3/4 cup, $1.50")
print("1 1/2 shredded, $1.35")
print("1 1/2 teaspoon, $1.95")
print("3/4 teaspoon, $2.55")
print("3, $2.55")
print("3 minced, $1.20")
print("2 1/4 pound, $10.50")
print("3/4 pound, $2.25")
print("1 1/2 chopped finely, $1.05")
print("3/4 teaspoon, $6.00")
print("1 1/2 teaspoon, $3.00")
print("4 1/8, $7.50")