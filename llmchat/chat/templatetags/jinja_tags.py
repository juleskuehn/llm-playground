from django_jinja import library
import jinja2
import markdown as md

# See https://niwi.nz/django-jinja/latest/#_registering_filters_in_a_django_way

@library.filter
def markdown(value):
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])
