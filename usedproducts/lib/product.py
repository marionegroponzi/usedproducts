import json
from typing import Optional
import re
from dataclasses import dataclass

@dataclass
class Product(object):
    description: str
    link: str
    price_str: str
    details: str = ""

    ### derived members
    clean_details: str = ""
    is_iphone: bool = False
    is_ipad: bool = False
    storage: str = ""
    model_name: str = ""
    battery_level: str = ""
    has_apple_garantie: bool = False
    price_num: float = 0.0

    def fill_derived(self):
        self.fill_price_num()
        self.fill_clean_details()
        self.fill_is_iphone()
        self.fill_is_ipad()
        self.fill_storage()
        self.fill_model_name()
        self.fill_battery_level()
        self.fill_has_apple_garantie()

    def fill_price_num(self):
        price = self.price_str
        for c in ['€',' ','-','\.']:
            price = re.sub(c, "", price)

        price = re.sub(",", ".", price)
        self.price_num = float(price)

    def fill_clean_details(self):
        d = re.sub("\n", " ", self.details)
        d = re.sub('-', ' ', d)
        d = re.sub("\s+", " ", d)
        d = re.sub("Omschrijving ", "", d, flags=re.IGNORECASE)
        d = re.split("JOUW PRODUCT INRUILEN", d, flags=re.IGNORECASE)[0]
        d = re.split("Te bezichtigen in onze winkel of verzenden", d, flags=re.IGNORECASE)[0]
        d = re.sub("NU TE KOOP BIJ.*:", '', d, flags=re.IGNORECASE)
        
        self.clean_details = d.strip()

    def fill_is_iphone(self) -> bool:
        self.is_iphone = re.search("iphone", self.description, flags=re.I) is not None
    
    def fill_is_ipad(self) -> bool:
        self.is_ipad = re.search("ipad", self.description, flags=re.I) is not None
    
    def fill_storage(self) -> Optional[str]:
        sizes = []
        for size in [64, 128, 256, 512]:
            sizes.append({'match': f"{size}.*gb", 'name': f"{size}gb"})

        for size in sizes:
            if re.search(size['match'], self.description, flags=re.I):
                self.storage = size['name']
                return

    
    def fill_model_name(self) -> Optional[str]:
        names = []
        models = []
        for i in range (11, 16):
            names.append(f"{i} pro max")
            names.append(f"{i} pro")
            names.append(f"{i} mini")
            names.append(f"{i} plus")
            names.append(f"{i}")

        names = names + ["xs max", "xs", "xr", "x", "x", "x", "6s", "6", "7 plus", "7"]

        names = names + ["se.*2022", "se.*2020"]

        for name in names:
            model_name = name.replace(".*", " ")
            models.append({'match': 'iphone ' + name, 'name': 'iphone ' + model_name})


        names = ["pro 12.9", "pro.*2022", "pro.*2018", "pro.*2017", "pro 11", "2021", "2020", "2019", "2018", "mini 6", "mini 5", "mini", "air 2022", "air 10.9", "9e gen", "8e gen", "10th gen", "air 3" "air 2", "air 1", "air", ]
        for name in names:
            model_name = name.replace(".*", " ")
            models.append({'match': 'ipad ' + name, 'name': 'ipad ' + model_name})

        for model in models:
            if re.search(model['match'], self.description, flags=re.I):
                self.model_name = model['name']
                return
    
    def fill_battery_level(self) -> Optional[str]:
        lvl = re.search(" (\d+)%", self.description, flags=re.I)
        if lvl:
            self.battery_level = lvl[1]
        else:
            lvl = re.search(" (\d+)%", self.details, flags=re.I)
            if lvl:
                self.battery_level = lvl[1]
    
    def fill_has_apple_garantie(self) -> bool:
        self.has_apple_garantie = re.search("apple garantie", self.description, flags=re.I) is not None

    def to_json(self):
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__, ensure_ascii=False)
    
