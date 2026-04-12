class ExternalProductSchema:
    def __init__(
        self,
        external_id,
        name,
        description,
        brand,
        price,
        currency,
        stock,
        category_path,
        specs,
        image_url,
    ):
        self.external_id = external_id
        self.name = name
        self.description = description
        self.brand = brand
        self.price = price
        self.currency = currency
        self.stock = stock
        self.category_path = category_path  # ["Electronics","Sensors","IMU"]
        self.specs = specs
        self.image_url = image_url
