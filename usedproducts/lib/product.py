from typing import Optional
import re

class Product(object):
    def __init__(self, description, link, price) -> None:
        self.description = description
        self.link = link
        self.price = price
        # self.is_iphone = Product.is_iphone(description)
        # self.is_ipad = Product.is_ipad(description)
        # self.battery_level = Product.battery_level(description)
        # self.model = Product.model_name(description)
        # self.memory = Product.memory(description)
        # self.has_apple_garantie = Product.has_apple_garantie(description)

    def is_iphone(text) -> bool:
        return re.search("iphone", text, flags=re.I) is not None
    
    def is_ipad(text) -> bool:
        return re.search("ipad", text, flags=re.I) is not None
    
    def memory(text) -> Optional[str]:
        sizes = []
        for size in [64, 128, 256, 512]:
            sizes.append({'match': f"{size}.*gb", 'name': f"{size}gb"})

        for size in sizes:
            if re.search(size['match'], text, flags=re.I):
                return size['name']
        return ""            

    
    def model_name(text) -> Optional[str]:
        names = []
        models = []
        for i in range (12, 16):
            names.append(f"{i} pro max")
            names.append(f"{i} pro")
            names.append(f"{i} mini")
            names.append(f"{i} plus")

        names = names + ["xs max", "xs", "xr", "x", "x", "x", "6s", "6"]

        names = names + ["se.*2022", "se.*2020"]

        for name in names:
            model_name = name.replace("*.", " ")
            models.append({'match': 'iphone ' + name, 'name': 'iphone ' + model_name})


        names = ["pro 12.9", "pro.*2022", "pro.*2018", "pro.*2017", "pro 11", "2021", "2020", "2019", "2018", "mini 6", "mini 5", "mini", "air 2022", "air 10.9", "9e gen", "8e gen", "10th gen", "air 3" "air 2", "air 1", "air", ]
        for name in names:
            model_name = name.replace("*.", " ")
            models.append({'match': 'ipad ' + name, 'name': 'ipad ' + model_name})

        for model in models:
            if re.search(model['match'], text, flags=re.I):
                return model['name']
        return ""
    
    def battery_level(text) -> Optional[str]:
        lvl = re.search("accu (\d+)", text, flags=re.I)
        if lvl:
            return lvl[1]
    
    def has_apple_garantie(text) -> bool:
        return re.search("apple garantie", text, flags=re.I) is not None
    
    def __str__(self):
        return self.description
    def __unicode__(self):
        return self.description
    def __repr__(self):
        return self.description
