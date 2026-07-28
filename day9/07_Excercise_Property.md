```
# DIY

Create a class *Item*, sku, name, quantity, unit_price 

sku and name are attributes
quantity and unit_price must be properties, _quantity, _unit_price
quantity > 0
unit_price > 0

__str__, like in csv format, P100, phone1, 1, 10000, 10000 (amount)
__repr__ to create Item again using eval

derived attribute _amount, must have only getter, not setter

@setter
  ..
   self.__calculate_amount()

def _calculate_amount():
    self._amount = self._unit_price * self._price

on the setter of quantity and unit_price, you must compute _amount



````
