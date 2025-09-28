# For-else loop example
print("For-else loop:")
for i in range(3):
    print(f"Number: {i}")
else:
    print("Loop completed normally")

print("\nFor-else with break:")
for i in range(5):
    if i == 2:
        print("Breaking at 2")
        break
    print(f"Number: {i}")
else:
    print("This won't print due to break")

# While-else loop example
print("\nWhile-else loop:")
count = 0
while count < 3:
    print(f"Count: {count}")
    count += 1
else:
    print("While loop finished")