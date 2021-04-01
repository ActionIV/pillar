# Create extra functions for print inventories only, print gold count, print status line by player

import pandas
import sys

path1 = r"FFL2 Data.xlsx"
path2 = r"Battle Log.xlsm"
workbook = pandas.ExcelFile(path1)
log = pandas.ExcelFile(path2)
players = log.parse("Players", index_col = 'Index')

text_path1 = "characters.log"
text_path2 = "inventory.log"
text_path3 = "status line.log"

players["Current HP"].fillna(-1, inplace = True, downcast = 'infer')
players["S0 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S1 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S2 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S3 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S4 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S5 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S6 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["S7 Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players["MAGI Uses Left"].fillna(-1, inplace = True, downcast = 'infer')
players.fillna("blank", inplace = True)

print("----------------------------------------")
print("1. Character Sheets")
print("2. Inventory & Gold")
print("3. Status Line")
print("----------------------------------------")
while True:
    option = int(input("Enter a number: "))
    try:
        option = int(option)
    except ValueError:
        option = input("Invalid entry.", end = " ")
        continue
    break

if option == 1:
    stdout = sys.stdout
    sys.stdout = open(text_path1, 'w')

    # Print Character Snapshots
    for count in range(len(players.index)):
        if players.iloc[count,0] == "blank" or players.iloc[count,2] == "NPC":
            pass
        else:
            print("%s || %s" % (players.iloc[count, 0], players.iloc[count, 2]))
            print("CLASS: %s" % players.iloc[count, 3])
            print("HP: %d | STR: %d | DEF: %d | AGL: %d | MANA: %d" % (players.iloc[count, 5],players.iloc[count, 7],
            players.iloc[count, 9],players.iloc[count, 11],players.iloc[count, 13]))
            print("[", end = "")
            skill = 14
            while skill < 38:
                if skill < 35:
                    if players.iloc[count,skill] == "blank":
                        print("EMPTY", end = ", ")
                    elif players.iloc[count,skill+1] in (-1, -2):
                        print(players.iloc[count,skill], end = ", ")
                    else:
                        print(players.iloc[count,skill], end = " - ")
                        print(players.iloc[count,skill+1], end = ", ")
                    skill += 3
                else:
                    if players.iloc[count,skill] == "blank":
                        print("EMPTY", end = "]\n")
                    elif players.iloc[count,skill+1] in (-1, -2):
                        print(players.iloc[count,skill], end = "]\n")
                    else:
                        print(players.iloc[count,skill], end = " - ")
                        print(players.iloc[count,skill+1], end = "]\n")
                    break
            print("MAGI: %s" % players.iloc[count, 38])
            print("OTHER MAGI: %s" % players.iloc[count, 41])
            print("INVENTORY: %s" % players.iloc[count,42])
            print("GOLD: %d" % players.iloc[count,43])
            print("")

    sys.stdout = stdout
    print("All done!")

elif option == 2:
    stdout = sys.stdout
    sys.stdout = open(text_path2, 'w')

    for count in range(len(players.index)):
        if players.iloc[count,0] == "blank" or players.iloc[count,2] == "NPC":
            pass
        else:
            print("%s || %s" % (players.iloc[count, 0], players.iloc[count, 2]))
            print("INVENTORY: %s" % players.iloc[count,42])
            print("GOLD: %d" % players.iloc[count,43])
            print("")

    sys.stdout = stdout
    print("All done!")

elif option == 3:
    commands = workbook.parse("Weapon", index_col = 'Index')
    stdout = sys.stdout
    sys.stdout = open(text_path3, 'w')

    for each in range(len(players.index)):
        if players.iloc[each, 2] == "NPC":
            pass
        else:
            print("| %s: %d/%d" % (players.iloc[each, 0], players.iloc[each, 4], players.iloc[each, 5]), end = " ")
            if players.iloc[each,44] == "blank":
                print("[", end = " ")
            else:
                print("%s" % players.iloc[each,44], end = " [")
            # Print skill counts at the end of a battle
            i=0
            pos = 14
            while i < 8:
                skill = players.iloc[each, pos]
                
                if players.iloc[each, pos+2] <= 0:
                    pass
                else:
                    skill = players.iloc[each, pos]
                    tar_type = commands.loc[skill, "Target Type"]
                    if tar_type == "All Enemies":
                        tar_type = "AE"
                    elif tar_type == "Ally":
                        tar_type = "A"
                    elif tar_type == "Allies":
                        tar_type = "AA"
                    elif tar_type == "Block":
                        tar_type = "D"
                    elif tar_type == "Counter":
                        tar_type = "C"
                    elif tar_type == "Single":
                        tar_type = "Si"
                    elif tar_type == "Sweep":
                        tar_type = "Sw"
                    elif tar_type == "Group":
                        tar_type = "G"
                    else:
                        tar_type == "U"
                    print("%s(%s)-%d" % (skill, tar_type, players.iloc[each,pos+1]), end = ", ")
                pos += 3
                i += 1
            print("]")

    sys.stdout = stdout
    print("All done!")    
else:
    pass