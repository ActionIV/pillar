import pandas
import random

path1 = r"FFL2 Data.xlsx"
workbook = pandas.ExcelFile(path1)
encounters = workbook.parse("Encounters")

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

    zone_table = encounters.loc[encounters["ZONE"] == zone]
    for row in range(encounters.shape[0]):
        if zone_table.iloc[row, 2] >= roll:
            range1 = str(zone_table.iloc[row, 4])
            num1 = rollGroupSize(range1)
            group1 = zone_table.iloc[row, 5]
            print("{ %s - %d" % (group1, num1), end = " ")
            if not pandas.isnull(zone_table.iloc[row, 6]):
                range2 = str(zone_table.iloc[row, 6])
                num2 = rollGroupSize(range2)
                group2 = zone_table.iloc[row, 7]
                print("| %s - %d" % (group2, num2), end = " ")
                if not pandas.isnull(zone_table.iloc[row, 8]):				
                    range3 = str(zone_table.iloc[row, 8])
                    num3 = rollGroupSize(range3)
                    group3 = zone_table.iloc[row, 9]
                    print("| %s - %d" % (group3, num3), end = " ")
            print("}")
            break
    gen = input("Generate another (y/n)?: ")