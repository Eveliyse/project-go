from django import template
from ..models import Category

register = template.Library()


@register.inclusion_tag('projects/explore_card_contents.html')
def category_links():
    categories = Category.objects.all()
    return {'categories': categories}
