import multiprocessing
import pymongo
from lib.product import Product


class DBManager(object):
    def __init__(self):
        self.coll = DBManager.get_mongo()

    def update_product_in_db(self, product: Product):
        product.set_verified_date()  
        self.coll.update_one({"link": product.link},{"$set": {"verified": product.verified }})

    def already_stored(self, product: Product):
        already_stored = self.coll.find_one({ "link": product.link })
        return already_stored != None    
    
    def save_to_mongo(self, product: Product):
        # pay attention that inserting the product modifies it. If you need to return it, copy the dict first
        d = product.__dict__
        self.coll.insert_one(d)

    def get_mongo() -> pymongo.collection.Collection:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        coll = client.usedproducts.products
        return coll    
    
    def clear(self):
        self.coll.delete_many({ })

    def save_product(self, q_incoming: multiprocessing.Queue):
        while(True):
            incoming = q_incoming.get()
            if type(incoming) is Product:
                # print(f"Saving product {incoming.name}")
                self.save_to_mongo(self, incoming, self.coll)
            if type(incoming) is str:
                print("Exiting save process")
                return
