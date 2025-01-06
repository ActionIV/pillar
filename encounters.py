import pandas
import random

path1 = r"FFL2 Data.xlsx"
workbook = pandas.ExcelFile(path1)
encounters = workbook.parse("Encounters")
INCREASE_RATE = 5

def rollGroupSize(text):
	roll_range = text.split("-")
	if len(roll_range) > 1:
		return random.randint(int(roll_range[0]), int(roll_range[1]))
	else:
		return 1

gen = "y"
while gen != "n":
    zone = input("Generate encounter for which zone: ")
    roll = random.randint(1,256)
    group1 = ""
    group2 = ""
    group3 = ""
    num1 = 0
    num2 = 0
    num3 = 0

    try:
	    encounters.loc[encounters["ZONE"] == zone]
    except KeyError:
	    zone = input("Invalid zone. Enter a new one: ")

    zone_table = encounters.loc[encounters["ZONE"] == zone]
    for row in range(encounters.shape[0]):
        if zone_table.iloc[row, 2] >= roll:
            range1 = str(zone_table.iloc[row, 4])
            num1 = rollGroupSize(range1)
            group1 = zone_table.iloc[row, 5]
            if num1 > 0:
                print("{ %s - %d" % (group1, num1), end = " ")
            if not pandas.isnull(zone_table.iloc[row, 6]):
                range2 = str(zone_table.iloc[row, 6])
                num2 = rollGroupSize(range2)
                group2 = zone_table.iloc[row, 7]
                if num2 > 0:
                    print("| %s - %d" % (group2, num2), end = " ")
                if not pandas.isnull(zone_table.iloc[row, 8]):				
                    range3 = str(zone_table.iloc[row, 8])
                    num3 = rollGroupSize(range3)
                    group3 = zone_table.iloc[row, 9]
                    if num3 > 0:
                        print("| %s - %d" % (group3, num3), end = " ")
            print("}")
            break

    steps_to_battle = 0
    current_chance = 0
    steps_taken = 0
    while steps_to_battle == 0:
        battle_roll = random.randint(1,100)
        if battle_roll < current_chance:
            steps_to_battle = steps_taken + 1
        else:
            current_chance += INCREASE_RATE
            steps_taken += 1
    print("Steps taken: %d" % steps_to_battle)

    gen = input("Generate another (y/n)?: ")