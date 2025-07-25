subjects = {"math": 25, "history": 37, "english": 99}

def sort_dict(dictionary):
    min_score = min(dictionary.values())
    for i in dictionary:
        if dictionary[i] == min_score:
            return i


print(sort_dict(subjects))
