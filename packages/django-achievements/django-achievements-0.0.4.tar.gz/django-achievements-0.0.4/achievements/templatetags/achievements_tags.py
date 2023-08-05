from achievements.utils import get_user_score
from django import template

register = template.Library()
                
@register.filter
def user_score(value):
	""" Get the achievements score for a given user"""
	return get_user_score(user=value)