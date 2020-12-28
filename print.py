# Create extra functions for print inventories only, print gold count, print status line by player

import pandas
import sys

path2 = r"Battle Log.xlsm"
log = pandas.ExcelFile(path2)
players = log.parse("Players", index_col = 'Index')

text_path = "characters.log"

stdout = sys.stdout
sys.stdout = open(text_path, 'w')

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