import random

def generate_random_numbers():
    numbers = []
    for _ in range(50):
        random_number = random.uniform(4.0, 7.0)
        numbers.append(random_number)
    return numbers

if __name__ == "__main__":
    numbers = generate_random_numbers()
    print(numbers)

    total = 0.0
    for value in numbers:
        total += value
    mean = total / len(numbers)

    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    if n % 2 == 1:
        median = sorted_nums[n // 2]
    else:
        median = (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2

    smallest = numbers[0]
    for value in numbers:
        if value < smallest:
            smallest = value

    # printing results
    print("Mean:")
    print(mean)
    print("Median:")
    print(median)
    print("Smallest value:")
    print(smallest)