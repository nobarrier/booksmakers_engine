from .models import Category


def global_categories(request):
    return {"categories": Category.objects.filter(parent__isnull=True)}
