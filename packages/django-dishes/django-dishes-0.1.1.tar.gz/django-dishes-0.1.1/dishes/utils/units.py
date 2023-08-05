# A simple file defining common units used in cooking
UNIT_CHOICES = ( ('foz', 'fluid ounce'), ('fc', 'fluid cup' ), ('pt', 'pint'), ('qt', 'quart'), ('G', 'gallon'),
                 ('oz', 'ounce'), ('c', 'cup'), ('lb', 'pound'), ('ts', 'teaspoon'), ('T', 'tablespoon'))

# Base units
kilogram = kilograms = 1
liter = liters = 1
gram = grams = 0.001 * kilogram
milligram = milligrams = 0.001 * gram
milliliter = milliliters = 0.001 * liter
kiloliter = kiloliters = 1000 * liter

# Crap-o imperial units
fluid_ounce = fluid_ounces = 1
fluid_cup = fluid_cups = 8 * fluid_ounces
pint = pints = 16 * fluid_ounces
quart = quarts = 32 * fluid_ounces
gallon = gallons = 128 * fluid_ounces

teaspoon = teaspoons = 0.1666666666667*fluid_ounces
tablespoon = tablespoons = 0.5*fluid_ounces


ounce = ounces = 1
pound = pounds = 16*ounces



