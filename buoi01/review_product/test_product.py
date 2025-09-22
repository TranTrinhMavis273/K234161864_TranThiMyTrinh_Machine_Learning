from product import Product
p1 = Product(id=1, name="xyz", price=1000, quantity=1)
print(p1)
p2= Product(id=2, name="abc", price=2000, quantity=2)
p1=p2
print('thong tin cua p1',p1)
p1.name="thay doi"
print('thong tin cua p2',p2)
