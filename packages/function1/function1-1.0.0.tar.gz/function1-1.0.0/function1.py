def function1(a):
    if a==1:
        return 1
    else:
        return a*function1(a-1)
 
