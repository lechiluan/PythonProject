import random
pass_Length = int(input("Enter the length of password: "))

s="abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"

p =  "".join(random.sample(s,passLength ))
print (p)