import csv
import os

from django.core.wsgi import get_wsgi_application

csv_filepathname = "ingredients.csv"
os.environ['DJANGO_SETTINGS_MODULE'] = 'foodgram_backend.settings'

application = get_wsgi_application()

dataReader = csv.reader(open(csv_filepathname, encoding='UTF-8'),
                        delimiter=',',
                        quotechar='"')
next(dataReader)

from app.models import Ingredient
for row in dataReader:
    ingredient = Ingredient()
    ingredient.name = row[0]
    ingredient.measurement_unit = row[1]
    ingredient.save()
