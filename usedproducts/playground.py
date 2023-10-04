
# import json
# from dataclasses import dataclass

# @dataclass
# class Student:
#     name: str
#     roll_no: int
#     addresses: list
   
#     def to_json(self):
#         return json.dumps(self, indent = 4, default=lambda o: o.__dict__)

# @dataclass
# class Address:
#     city: str
#     street: str
#     pin: str
          
# address1 = Address("Bulandshahr", "Adarsh Nagar", "203001")
# address2 = Address("Bulandshahr", "Adarsh Nagar", "203001")
# student = Student("Raju", 53, [address1, address2])
  
# # Encoding
# student_json = student.to_json()
# print(student_json)
# print(type(student_json))
  
# # Decoding
# student = json.loads(student_json)
# print(student)
# print(type(student))




# # import argparse


# # parser = argparse.ArgumentParser(
# #     prog='usedproducts',
# #     description='Crawler and analyzer for userdproducts.com',
# #     )
# # parser.add_argument('--max_pages', '-m', type=int, help='maximum number of pages to load')
# # args = parser.parse_args()
# # print(args.max_pages > 3)

# class Test:
#     def __init__(self):
#         self.one = ""
#         self.two = 2

# print(Test().__dict__)


#### mongo db
import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

products_col = myclient.usedproducts.products
# print(type(products_col))

# mydb = myclient["usedproducts"]
# if mydb is None:
#     print("mydb not found")
#     exit(-1)

# products_col = mydb["products"]
# if products_col is None:
#     print("products_col not found")
#     exit(-1)

# mydict = { "name": "John", "address": None }
# print(mydict)
# x = products_col.insert_one(mydict)
# print(mydict)

class Test:
    def __init__(self):
        self.name = "name"
        self.surname = "surname"

t = Test()
d = t.__dict__
print(d)
x = products_col.insert_one(d.copy())
print(t.__dict__)

####
# from typing import Callable


# def echo(x):
#     print(x)

# def echoplus(x):
#     print(x+1)

# def mycall(myfunc: Callable[[int], None]):
#     myfunc(3)

# mycall(echo)
# mycall(echoplus)