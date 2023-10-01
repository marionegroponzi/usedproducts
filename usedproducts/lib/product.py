from typing import Optional
import re
from dataclasses import dataclass
@dataclass
class Product(object):
    description: str
    link: str
    price: str
    details: str

    def clean_details(self):
        d = ' '.join(self.description.split())
        d = d.lstrip("Omschrijving ")
        d = re.split("JOUW PRODUCT INRUILEN", d, flags=re.IGNORECASE)[0]
        d = re.split("Te bezichtigen in onze winkel of verzenden", d, flags=re.IGNORECASE)[0]
        d = re.sub("NU TE KOOP BIJ.*:", '', d, flags=re.IGNORECASE)
        d = d.replace('--','').strip()
        return d

    def is_iphone(self) -> bool:
        return re.search("iphone", self.description, flags=re.I) is not None
    
    def is_ipad(self) -> bool:
        return re.search("ipad", self.description, flags=re.I) is not None
    
    def memory(self) -> Optional[str]:
        sizes = []
        for size in [64, 128, 256, 512]:
            sizes.append({'match': f"{size}.*gb", 'name': f"{size}gb"})

        for size in sizes:
            if re.search(size['match'], self.description, flags=re.I):
                return size['name']
        return ""            

    
    def model_name(self) -> Optional[str]:
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
            if re.search(model['match'], self.description, flags=re.I):
                return model['name']
        return ""
    
    def battery_level(self) -> Optional[str]:
        lvl = re.search("accu (\d+)", self.description, flags=re.I)
        if lvl:
            return lvl[1]
    
    def has_apple_garantie(self) -> bool:
        return re.search("apple garantie", self.description, flags=re.I) is not None
    
