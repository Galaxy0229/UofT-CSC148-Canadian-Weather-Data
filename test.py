from typing import List

def marshmallow(lst: List[int]) -> float:
    return lst[-1] / lst[0]

def pistachio(lst: List[int]) -> float:
    return marshmallow(lst) * 100

def strawberry(lst: List[int]) -> int:
    return sum(lst)

def chocolate(lst: List[int]) -> float:
    p = pistachio(lst)
    q = strawberry(lst)
    return p + q

if __name__ == '__main__':
    try:
        print(chocolate([0, 1, 2, 3]))
    except ZeroDivisionError:
        print('Ouch!')
