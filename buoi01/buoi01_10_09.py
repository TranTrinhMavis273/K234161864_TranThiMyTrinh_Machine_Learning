def ptbac1 (a,b):
    '''
    a: he so a
    b: he so b
    return: la nghiem theo a va b
    '''
    if a==0 and b==0:
        return "vo so nghiem"
    elif a==0 and b!=0:
        return "vo nghiem"
    else: 
        return -b/a 

ket_qua=ptbac1(2,5)
print("nghiem cua phuong trinh la", ket_qua)
''''''
def fibonacci(n): 
    if n<=2:
        return 1
    return fibonacci(n-1)+ fibonacci(n-2)
def pick_fib(n):
    nth_fib = fibonacci(n)
    fib_list = []
    for i in range(1, n + 1):
        fib_list.append(fibonacci(i))
    return nth_fib, fib_list

x, y = pick_fib(6)
print("list tu 1 den 6 la", y)    
   
''''''



