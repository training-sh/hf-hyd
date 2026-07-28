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

```python
class Item:
    def __init__(self, sku, name, unit_price, quantity):
        self.sku = sku #  is attribute
        self.name = name # name is attribute
        self.quantity = quantity
        self.unit_price = unit_price
        

    @property
    def unit_price(self):
        return self._unit_price

    @unit_price.setter
    def unit_price(self, value):
        """Validate and store a product price."""
        print ("price setter called with value ", value)
        value = float(value)
        if value <= 0:
            raise ValueError("price must be greater than zero")
        
        self._unit_price = value

        self._calculate_amount()

    @property
    def quantity(self):
            return self._quantity
    
    @quantity.setter
    def quantity(self, value):
        value = int(value)
        if value <= 0:
            raise ValueError("qty must be greater than zero")
        
        self._quantity = value
        self._calculate_amount()

    @property
    def amount(self):
        return self._amount

    def _calculate_amount(self):
        if ('_quantity' in self.__dict__) and ('_unit_price' in self.__dict__):
            self._amount = self.unit_price * self.quantity

item = Item("P101", 'Phone1', 10000, 2)

print (item.amount)

item.quantity = 3

print (item.amount)
```
