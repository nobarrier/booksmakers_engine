from apps.catalog.models import Category, CategoryRule


def build_text_blob(product_data):
    category_path = product_data.get("category_path") or []

    if isinstance(category_path, list):
        category_text = " ".join([str(x) for x in category_path])
    else:
        category_text = str(category_path)

    text_blob = " ".join(
        [
            str(product_data.get("manufacturer", "")),
            str(product_data.get("description", "")),
            str(product_data.get("mpn", "")),
            str(product_data.get("dk_part", "")),
            category_text,
        ]
    )

    return text_blob.upper()


def get_root_category(category_name):
    return Category.objects.filter(
        name=category_name,
        parent=None,
        is_active=True,
    ).first()


def get_or_create_child_category(category_name, parent):
    if not parent:
        return None

    category, _ = Category.objects.get_or_create(
        name=category_name,
        parent=parent,
        defaults={
            "slug": "",
            "is_active": True,
        },
    )

    return category


def auto_assign_category(product_data):
    """
    CategoryRule 기반 정식 자동 분류 엔진.

    원칙:
    1. CategoryRule DB를 기준으로 분류한다.
    2. 1차 카테고리는 기존 Category만 사용한다.
    3. 2차/3차 카테고리는 필요한 경우 생성한다.
    4. priority가 높은 룰을 먼저 적용한다.
    5. 매칭 실패 시 None 반환한다.
    """

    text_blob = build_text_blob(product_data)

    rules = CategoryRule.objects.order_by("-priority", "level", "id")

    level1 = None
    level2 = None
    level3 = None

    for rule in rules:
        keyword = (rule.keyword or "").strip().upper()
        category_name = (rule.category_name or "").strip()

        if not keyword or not category_name:
            continue

        if keyword not in text_blob:
            continue

        if rule.level == 1:
            found = get_root_category(category_name)
            if found:
                level1 = found
                level2 = None
                level3 = None

        elif rule.level == 2:
            if level1:
                level2 = get_or_create_child_category(category_name, level1)
                level3 = None

        elif rule.level == 3:
            if level2:
                level3 = get_or_create_child_category(category_name, level2)

    return level3 or level2 or level1
