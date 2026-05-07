from django.db.models import Case, IntegerField, Value, When

from apps.catalog.models import Category


def global_categories(request):
    categories = (
        Category.objects.filter(parent=None, is_active=True)
        .annotate(
            uncategorized_last=Case(
                When(name="Uncategorized", then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        .prefetch_related("children")
        .order_by("uncategorized_last", "name")
    )

    return {
        "categories": categories,
    }
