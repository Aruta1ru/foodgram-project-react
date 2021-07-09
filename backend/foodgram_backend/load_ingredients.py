import csv
import os
import sys

from django.core.wsgi import get_wsgi_application

csv_filepathname="C:/Dev/foodgram-project-react/data/ingredients.csv"
your_djangoproject_home="C:/Dev/foodgram-project-react/foodgram_backend"

sys.path.append(your_djangoproject_home)
os.environ['DJANGO_SETTINGS_MODULE'] = 'foodgram_backend.settings'

application = get_wsgi_application()

from app.models import Ingredient

dataReader = csv.reader(open(csv_filepathname, encoding='UTF-8'), delimiter=',', quotechar='"')
next(dataReader)

for row in dataReader:
    ingredient = Ingredient()
    ingredient.name = row[0]
    ingredient.measurement_unit = row[1]
    ingredient.save()