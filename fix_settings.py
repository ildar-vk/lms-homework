import re

with open('lms_project/settings.py', 'r') as f:
    content = f.read()

if "'django_filters'" not in content and '"django_filters"' not in content:
    content = content.replace(
        "'rest_framework',",
        "'rest_framework',\n    'django_filters',"
    )
    
with open('lms_project/settings.py', 'w') as f:
    f.write(content)
    
print("✓ django_filters added to INSTALLED_APPS")
