from achievements.models import load_classes

def achievements_aware(func):
	load_classes()
	return func