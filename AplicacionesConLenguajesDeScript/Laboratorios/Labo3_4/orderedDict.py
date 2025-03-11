from collections import OrderedDict

n = int(input().strip())

items = OrderedDict()

for _ in range(n):
    *item_name, price = input().split()
    item_name = " ".join(item_name)
    price = int(price)

    items[item_name] = items.get(item_name, 0) + price

for item, net_price in items.items():
    print(item, net_price)