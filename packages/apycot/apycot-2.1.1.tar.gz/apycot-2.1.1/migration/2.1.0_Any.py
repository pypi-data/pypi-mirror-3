
from cubes.apycot import recipes

if not rql('Recipe R WHERE R name "apycot.recipe.debian"'):
    recipes.create_debian_recipe(session)
if not rql('Recipe R WHERE R name "apycot.recipe.experimental"'):
    recipes.create_experimental_recipe(session)
