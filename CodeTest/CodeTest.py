# n = int(input("Enter element of arrays: "))
# # Case 1: using for loop
# # arr = []
# # for i in range(0,n):
# #     arr.append((int(input())))
# # print("Array: ", arr)
# # Case 2: using list comprehension
# arr = map(int, input("Enter values of array: ").split())
# print("Array: ", list(arr))

n = int(input("Enter factorial of number: "))
fact = 1
for i in range(fact, n+1):
    fact = fact * i
print("Factorial: ", fact)
    