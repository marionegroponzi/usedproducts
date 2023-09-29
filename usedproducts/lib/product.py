from typing import Optional
import re

class Product(object):
    def __init__(self, description, link, price) -> None:
        self.description = description
        self.link = link
        self.price = price
        self.is_phone = Product.is_iphone(description)
        self.model = Product.model_name(description)

    def is_iphone(text) -> bool:
        return re.match("iphone", text, flags=re.I) is not None
    
    def model_name(text) -> Optional[str]:
        models = []
        for i in range (12, 15):
            models.append(f"iphone {i} pro max")
            models.append(f"iphone {i} pro")
            models.append(f"iphone {i} mini")
            models.append(f"iphone {i}")
        for model in models:
            if re.match(model, text, flags=re.I):
                return model
        return ""
    
    def battery_level(self) -> Optional[str]:
        lvl = re.search("accu (\d+)", self.description, flags=re.I)
        if lvl:
            return lvl[1]
    
    def has_apple_garantie(self) -> bool:
        return re.match("apple garantie", self.description, flags=re.I) is not None
    
    def __str__(self):
        return self.description
    def __unicode__(self):
        return self.description
    def __repr__(self):
        return self.description
