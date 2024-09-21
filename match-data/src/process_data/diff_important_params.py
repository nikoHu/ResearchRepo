import ijson
import json
import csv
import random


def main():
    user_type_1_path = "../../cleaned_data/user_type_1.csv"
    user_type_1_ids = load_random_users(user_type_1_path)

    user_type_2_path = "../../cleaned_data/user_type_2.csv"
    user_type_2_ids = load_random_users(user_type_2_path)

    fitting_path = "../../data/fittings.json"
    important_params = count_fitting_params(user_type_1_ids, fitting_path)
    for param in important_params:
        print(param)


def count_fitting_params(user_ids, file_path):
    with open(file_path, "r") as file:
        fittings = {str(fitting["user_id"]): fitting for fitting in list(ijson.items(file, "RECORDS.item"))}
        user_a = extract_fitting_dict(json.loads(fittings[user_ids[0]]["fitting_content"]))
        user_b = extract_fitting_dict(json.loads(fittings[user_ids[1]]["fitting_content"]))
    return compare_dicts(user_a, user_b)


def compare_dicts(dict1, dict2):
    count_diff = []

    for key in dict1.keys():
        if key in dict2:
            if dict1[key] != dict2[key]:
                count_diff.append(key)
    return count_diff


def extract_fitting_dict(fitting):
    result = {}
    for key, values in fitting.items():
        for param, value in values.items():
            result[f"{key}_{param}"] = value
    return result


def load_random_users(file_path):
    with open(file_path, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        total_user_ids = list(reader)

    random_users = random.sample(total_user_ids, 2)
    user_ids = [str(user[0]) for user in random_users]
    return user_ids


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


if __name__ == "__main__":
    main()
