from typing import Optional
import re

class Product(object):
    def __init__(self, description, link, price) -> None:
        self.description = description
        self.link = link
        self.price = price
        self.is_iphone = Product.is_iphone(description)
        self.battery_level = Product.battery_level(description)
        self.model = Product.model_name(description)
        self.memory = Product.memory(description)
        self.has_apple_garantie = Product.has_apple_garantie(description)

    def is_iphone(text) -> bool:
        return re.search("iphone", text, flags=re.I) is not None
    
    def memory(text) -> Optional[str]:
        sizes = []
        for size in [64, 128, 256, 512]:
            sizes.append({'match': f"{size}.*gb", 'name': f"{size}gb"})

        for size in sizes:
            if re.search(size['match'], text, flags=re.I):
                return size['name']
        return ""            

    
    def model_name(text) -> Optional[str]:
        models = []
        for i in range (12, 16):
            name = f"iphone {i} pro max"
            models.append({'match': name, 'name': name})
            name = f"iphone {i} pro"
            models.append({'match': name, 'name': name})
            name = f"iphone {i} mini"
            models.append({'match': name, 'name': name})
            name = f"iphone {i} plus"
            models.append({'match': name, 'name': name})            
            name = f"iphone {i}"
            models.append({'match': name, 'name': name})

        models.append({'match': "iphone se.*2022", 'name': "iphone se (2022)"})
        models.append({'match': "iphone se.*2020", 'name': "iphone se (2020)"})
        name = f"iphone xs max"
        models.append({'match': name, 'name': name})
        name = f"iphone xs"
        models.append({'match': name, 'name': name})
        name = f"iphone xr"
        models.append({'match': name, 'name': name})
        name = f"iphone x"
        models.append({'match': name, 'name': name})
        name = f"iphone 8"
        models.append({'match': name, 'name': name})
        name = f"iphone 7"
        models.append({'match': name, 'name': name})
        name = f"iphone 6s"
        models.append({'match': name, 'name': name})
        name = f"iphone 6"
        models.append({'match': name, 'name': name})

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
