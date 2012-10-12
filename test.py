def someFunction(value, callback) :
    result = pow(value,2)
    callback(result)

def myFunction():
    v = 42
    someFunction(v, myFunction_continue)

def myFunction_continue(result):
    print result

myFunction()



def wrapper1(func, *args): # with star
    func(*args)

def wrapper2(func, args): # without star
    func(*args)

def func2(x, y, z):
    print x+y+z

wrapper1(func2, 1, 2, 3)
wrapper2(func2, [1, 2, 3])