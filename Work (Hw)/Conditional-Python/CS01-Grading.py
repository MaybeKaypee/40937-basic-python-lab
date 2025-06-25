x=int(input())+int(input())+int(input())
print("F" if x < 50 else "D" if x <= 54 else "D+" if x <= 59 else "C" if x <=64 else "C+" if x <= 69 else "B" if x <= 74 else "B+" if x<= 79 else "A" if x>=80 else "")


#print("your grade is "+"F D D+ C C+ B B+ A".split()[sorted((0,7,int(input("input score: "))//5-9))[1]])