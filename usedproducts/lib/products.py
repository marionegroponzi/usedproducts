import openpyxl
import json

class Products(object):
    def __init__(self) -> None:
        self.products = []

    def append(self, product):
        self.products.append(product)

    def save_to_excel(self):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        index = 1
        sheet.cell(row=index, column=2).value = "URI"
        sheet.cell(row=index, column=3).value = "Text"
        sheet.cell(row=index, column=4).value = "Price"
        sheet.cell(row=index, column=5).value = "iPhone"
        sheet.cell(row=index, column=6).value = "Battery"
        sheet.cell(row=index, column=7).value = "Apple Garantie"
        for index in range(2, len(self.products)+1):
            p = self.products[index-1]
            sheet.cell(row=index, column=2).value = p.link
            sheet.cell(row=index, column=3).value = p.description
            sheet.cell(row=index, column=4).value = p.price

        workbook.save("usedproducts.xlsx")

    def __str__(self):
        s = ''
        for product in self.products:
            s += str(product) +'\n'
        return s
    def __unicode__(self):
        return self.__str__()
    def __repr__(self):
        return self.__str__()

class ProductsEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__