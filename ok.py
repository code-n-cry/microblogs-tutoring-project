import random, math, tkinter


subjects = {"math": 51, "history": 32, "english": 356, "russian": 100}

def sort_dict(dictionary):
    min_score = min(dictionary.values())
    max_score = max(dictionary.values())
    sinus = math.sin(math.radians(30))
    for i in dictionary:
        if dictionary[i] == min_score:
            return i


print(sort_dict(subjects))
