from pickle import FALSE, TRUE
import pandas
import random
import operator

from sqlalchemy import true

path1 = r"FFL2 Data.xlsx"
path2 = r"Battle Log.xlsm"

workbook = pandas.ExcelFile(path1)
log = pandas.ExcelFile(path2)

players = log.parse("Players", index_col = 'Index')

monsters = workbook.parse("Monster", index_col = 'Index')
transformations = workbook.parse("Evolve")

monster_race_cap = 35

# TRANSFORMATIONS
more = "y"
while more != "n":
    not_monsters = ["Human", "Mutant", "Robot"]
    monster_players = players[players["CLASS"].isin(not_monsters) == False]
    mp = monster_players.loc[players["PLAYER"].isin(["NPC"]) == False]
    print(mp["CLASS"])
    who = input("Transform which character?: ")
    if who == "Test":
        current_monster = input("Starter class?: ")
    else:
        current_monster = mp.loc[who, "CLASS"]
    meat = input("Meat from which monster?: ")  #Add option to allow numeric entry for family. If numeric, ask for DS
    if meat == "debug":
        meat = int(input("Enter number 0-35: "))

    meat_type = ""
    meat_class = 0
    meat_add = 0
    meat_subtract = 0
    meat_skip = FALSE
    current_ds = 0
    current_class = 0
    current_type = ""
    new_monster = ""
    type_diff = 0
    variant = False
    variation = ""
#    transformation_list = mp.loc[who,"CLASS NOTES"]
#    count = transformation_list.count(",")
    minimum_level = 1+int(mp.loc[who,"CLASS NOTES"]/18)

    if type(meat) == int:
        meat_ds = int(input("DS level: "))
        meat_class = transformations.loc[meat,"FAMILY"]
        meat_type = transformations.loc[meat,"MEAT TYPE"]
        meat_add = transformations.loc[meat,"ADD"]
        meat_subtract = transformations.loc[meat,"SUBTRACT"]
        meat_skip = TRUE

    for row in range(transformations.shape[0]):
        for col in range(transformations.shape[1]):
            if transformations.iloc[row,col] == meat and meat_skip == FALSE:
                meat_ds = transformations.iloc[row,col+1]
                meat_class = transformations.loc[row,"FAMILY"]
                meat_type = transformations.loc[row,"MEAT TYPE"]
                meat_add = transformations.loc[row,"ADD"]
                meat_subtract = transformations.loc[row,"SUBTRACT"]
            if transformations.iloc[row,col] == current_monster:
                current_ds = transformations.iloc[row,col+1]
                current_class = transformations.loc[row,"FAMILY"]
                current_type = transformations.loc[row,"MEAT TYPE"]

    if current_type in ("A", "B") and meat_type == "C":
        type_diff = 1
    elif current_type in ("B", "C") and meat_type == "A":
        type_diff = -1

    next_class = int(current_class + meat_add + type_diff)
    if next_class > monster_race_cap:
        next_class = int(current_class + meat_subtract + type_diff)

    max_ds = max(current_ds, meat_ds)

    family_tree = []
    col = 4
    while col < transformations.shape[1]:
        if not pandas.isnull(transformations.iloc[next_class,col]):
            family_tree.append(tuple((transformations.iloc[next_class,col], transformations.iloc[next_class,col+1])))
        col += 2

    for member in range(len(family_tree)):
        # If first family member has a higher DS than the max DS the transformation will allow, take the first family member
        if member == 0 and max_ds <= family_tree[member][1]:
            new_monster = family_tree[member][0]
            break
        # If the max DS is less than the non-first family member, calculate the gap and decide which member is the resultant transformation
        elif max_ds < family_tree[member][1]:
            gap_up = family_tree[member][1] - meat_ds
            gap_down = meat_ds - family_tree[member-1][1]
            if gap_up <= gap_down:
                new_monster = family_tree[member][0]
            # If the new monster is below the minimum level threshold, transform back into current form
            elif family_tree[member-1][1] < minimum_level:
                new_monster = current_monster
            else:
                new_monster = family_tree[member-1][0]
            break
        # If the max DS matches the family member, that's the result
        else:
            new_monster = family_tree[member][0]

    new_HP = monsters.loc[new_monster, "HP"]
    new_Str = monsters.loc[new_monster, "Str"]
    new_Agl = monsters.loc[new_monster, "Agl"]
    new_Mana = monsters.loc[new_monster, "Mana"]
    new_Def = monsters.loc[new_monster, "Def"]
    ds_diff = current_ds - monsters.loc[new_monster, "DS"]
    stat_increase = 0

    if monsters.loc[new_monster, "DS"] <= current_ds and current_ds < 11 and random.randint(1,2) == 2:
        variant = True
        variant_roll = random.randint(1,11)
        if variant_roll < 6:
            variation = "Increased stats."
            stat_increase = 1 + max((5*ds_diff)/100,0.1)
            new_HP = int(new_HP * stat_increase)
            new_Str = max(new_Str + 1, int(new_Str * stat_increase))
            new_Agl = max(new_Agl + 1, int(new_Agl * stat_increase))
            new_Mana = max(new_Mana + 1, int(new_Mana * stat_increase))
            new_Def = max(new_Def + 1, int(new_Def * stat_increase))
        elif variant_roll < 11:
            variation = "Evolved skill."
        else:
            variation = "Increased stats and evolved skill."
            stat_increase = 1 + max((5*ds_diff)/100,0.1)
            new_HP = int(new_HP * stat_increase)
            new_Str = int(new_Str * stat_increase)
            new_Agl = int(new_Agl * stat_increase)
            new_Mana = int(new_Mana * stat_increase)
            new_Def = int(new_Def * stat_increase)
    
    print("%s eats %s meat. Changed from %s to %s." % (who, meat, current_monster, new_monster), end = " ")
    if variant == True:
        print("VARIANT: %s" % variation)
    else:
        print('\n')
    print("HP: %d | STR: %d | AGL: %d | MANA: %d | DEF: %d" % (new_HP, new_Str, new_Agl, new_Mana, new_Def))
    print("[", end = "")
    for skill in range(8):
        if skill < 7:
            print(monsters.loc[new_monster, "S%d" % skill], end = ", ")
        else:
            print(monsters.loc[new_monster, "S%d" % skill], end = "]\n")

    more = input("Another transformation? (y/n): ")


#print("Current: %s | Meat Class: %d | Meat Type: %s" % (current_class, meat_class, meat_type))