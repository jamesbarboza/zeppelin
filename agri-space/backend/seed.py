import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrispace.settings')
django.setup()

from apps.users.models import User
from apps.plots.models import CropTag, Plot
from django.contrib.gis.geos import Point

# Crop tags
tags = [
    ('Maize', 'row_crop'), ('Wheat', 'row_crop'), ('Soybeans', 'row_crop'),
    ('Tomatoes', 'horticulture'), ('Peppers', 'horticulture'), ('Potatoes', 'horticulture'),
    ('Apples', 'orchard'), ('Citrus', 'orchard'),
    ('Grass', 'pasture'), ('Alfalfa', 'pasture'),
]
for name, cat in tags:
    CropTag.objects.get_or_create(name=name, defaults={'category': cat})
print(f'Crop tags: {CropTag.objects.count()} total')

# Admin user
if not User.objects.filter(email='admin@agrispace.com').exists():
    User.objects.create_user(
        email='admin@agrispace.com', password='admin1234',
        role='admin', farm_name='Admin', is_staff=True, is_superuser=True,
    )
    print('Admin created: admin@agrispace.com / admin1234')
else:
    print('Admin already exists')

# Demo farmer
if not User.objects.filter(email='farmer@demo.com').exists():
    farmer = User.objects.create_user(
        email='farmer@demo.com', password='farmer1234', farm_name='Green Acres',
    )
    maize = CropTag.objects.get(name='Maize')
    wheat = CropTag.objects.get(name='Wheat')
    plot = Plot.objects.create(owner=farmer, name='North Field', geometry=Point(28.05, -26.1))
    plot.crop_tags.set([maize, wheat])
    print('Farmer created: farmer@demo.com / farmer1234')
    print(f'Demo plot created: {plot.name}')
else:
    print('Demo farmer already exists')

print('Seed complete.')
