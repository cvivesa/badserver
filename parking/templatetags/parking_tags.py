from django import template

register = template.Library()

@register.inclusion_tag('tags/chart.html')
def chart(title, url_name):
    return {
        'title': title,
        'url_name': url_name,
    }
