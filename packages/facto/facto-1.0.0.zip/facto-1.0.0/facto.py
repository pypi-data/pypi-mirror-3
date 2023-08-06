""" this is a recursive function to count the factorial of the integer number,
the function prompts the ser to input an integer, then 
it takes the argument and and print the argument and the value of it's factorial"""
def f(number):
        if (number==1):
            return number
        else:
            return number*f(number-1)
    
def facto():
    i = int( input ('please input an integer greater that 1: ' )) 
    print(f(i))
    
