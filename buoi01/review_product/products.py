class ListProduct:
    def __init__(self):
        self.products = []

    def add_product(self, product):
        self.products.append(product)

    def display_products(self):
        for product in self.products:
            print(product)
    def sap_xep_giam_dan(self):
        for i in range (0, len(self.products)):
            for j in range (i+1, len(self.products)):
                pi=self.products[i]
                pj=self.products[j]
                if pi.price < pj.price: 
                    self.products[i] = self.products[j]
                    self.products[j] = self.products[i] 
    def sap_xep_giam_dan_2 (self):
        self.products.sort(key=lambda x: x.price, reverse=True)