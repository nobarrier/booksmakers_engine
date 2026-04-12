from apps.catalog.models import Category, CategoryRule


def auto_assign_category(product_data):
    text_blob = " ".join(
        [
            str(product_data.get("manufacturer", "")),
            str(product_data.get("description", "")),
            str(product_data.get("mpn", "")),
        ]
    ).upper()

    rules = CategoryRule.objects.order_by("level")

    level1 = None
    level2 = None
    level3 = None

    for rule in rules:
        if rule.keyword.upper() in text_blob:

            # 🔹 1차는 반드시 기존 것에서만 찾기 (생성 금지)
            if rule.level == 1:
                level1 = Category.objects.filter(
                    name=rule.category_name, parent=None
                ).first()

            # 🔹 2차는 생성 가능
            elif rule.level == 2 and level1:
                level2, _ = Category.objects.get_or_create(
                    name=rule.category_name,
                    parent=level1,
                )

            # 🔹 3차도 생성 가능
            elif rule.level == 3 and level2:
                level3, _ = Category.objects.get_or_create(
                    name=rule.category_name,
                    parent=level2,
                )

    return level3 or level2 or level1
