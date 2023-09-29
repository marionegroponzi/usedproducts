from typing import Optional
import re

class Product(object):
    def __init__(self, description, link, price) -> None:
        self.description = description
        self.link = link
        self.price = price
        self.is_phone = Product.is_iphone(description)

    def is_iphone(text) -> bool:
        return re.match("iphone", text, flags=re.I) is not None
    
    def model_name(self) -> Optional[str]:
        if self.is_iphone():
            name = re.match("iphone (\w+)", self.description, flags=re.I)
            if name:
                return name[0]
    
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
