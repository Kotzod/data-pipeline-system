def calc_price():
    print("Consumption (units)?")
    units = float(input())

    print("Unit price (currency units)?")
    unit_price = float(input())

    partial_price = units * unit_price * 1.17

    if units < 500 :
        total_price = partial_price + 4.32
        print(f"Total price (currency units): {total_price:.2f}")
    else:
        total_price = partial_price + 7.75 
        print(f"Total price is {total_price:.2f} currency units.")

calc_price()