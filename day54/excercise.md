```
# Excercises

# implement power function lambnda n: n * n
# implement gst function that accept 3 parameters, amount float, discount int, tax int

def gst(amount, discount, tax):
    discounted_amount = amount * (1 - discount / 100)
    return discounted_amount * (1 + tax / 100)

```


