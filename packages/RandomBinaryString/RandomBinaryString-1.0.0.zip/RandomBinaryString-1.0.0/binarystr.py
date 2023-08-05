""" This is the "randombinarystring.py" module and it provides one function
called random_binary() which prints a random binary string of 5 charcaters."""


def binary_str():

    """ This function creates a empty string of 5 characters and it replaces
    each of the empty characters with a '0' or a '1'."""

    import random

    random.seed()

    string = ''
    for x in range(5):
        string += str(random.randint(0, 1))

    print(string)


