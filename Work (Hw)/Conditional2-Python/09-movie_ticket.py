x = int(input())
y = int(input())
z = 0
if x < 13:
    z = 100
elif x > 60:
    z = 120
else:
    z = 180

if (y == 6 or y == 7):
    print(z+50)
else:
    print(z)