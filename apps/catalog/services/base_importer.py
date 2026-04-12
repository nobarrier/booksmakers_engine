from dataclasses import dataclass


@dataclass
class NormalizedItem:
    supplier_code: str
    supplier_part_number: str
    manufacturer: str
    mpn: str
    name: str
    price: float
    stock: int
    url: str
    category_path: list[str] | None = None
    image_url: str | None = None
