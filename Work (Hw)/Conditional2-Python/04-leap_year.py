x = int(input())
if ((x%4==0)and((x%100==0)and(x%400==0))):
    print("Leap year")
else:
    print("Not leap year")
