
from django import template
from placemate_app.utils.helper_utils import get_batch_year  # import from your utils

register = template.Library()

@register.filter
def get_student_batch(student):
    return get_batch_year(student)