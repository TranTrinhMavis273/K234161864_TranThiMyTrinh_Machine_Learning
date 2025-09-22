
from products import ListProduct
from product import Product
lp = ListProduct()
lp.add_product(Product(id=1, name="xyz", price=100, quantity=1))
lp.add_product(Product(id=2, name="xyz", price=1110, quantity=22))
lp.add_product(Product(id=3, name="xyz", price=12220, quantity=333))
lp.add_product(Product(id=4, name="xyz", price=1044543, quantity=444))
lp.add_product(Product(id=5, name="xyz", price=10, quantity=55555))
lp.add_product(Product(id=6, name="xyz", price=1400, quantity=66))
print('danh sach san pham')
lp.display_products()
lp.sap_xep_giam_dan()
print('danh sach san pham sau khi sap xep')
lp.display_products()
lp.sap_xep_giam_dan_2()
print('danh sach san pham sau khi sap xep lan 2')
lp.display_products()