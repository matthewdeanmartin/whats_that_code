import math

squares = [x * x for x in range(10) if x % 2 == 0]
total = sum(squares)
print(math.sqrt(total))
