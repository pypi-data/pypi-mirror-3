"""The following modules contains basic arithmetic functions for manipulating
numbers."""
def factorialOfNumber(number):
    """ This function accepts a positional argument number and prints out the 
    factorial of the number to the screen"""
    noSet = number
    for each_item in range(number-1,1,-1):
        noSet = noSet*each_item
    print(noSet)
def factorialUsingRecursion(number):
    """This function accepts a positional argument number and prints out the 
    factorial of the number to the screen. It uses Recursion"""
    if(number ==1):
        return 1
    else:
        return number* factorialUsingRecursion(number -1)
