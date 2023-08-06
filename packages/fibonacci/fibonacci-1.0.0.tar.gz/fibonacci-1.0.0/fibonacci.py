""" a test function of fibonacci number """

def fibo(n):
    if n<2:
        return n;
    else:
        last = 1;
        last2 = 0;
        result= 0;
        for i in range(2,n+1):
            result = last + last2;
            last2 = last;
            last = result;
        return result;
