import json
import ijson
import time
import csv

from tqdm import tqdm


def main():
    start = time.time()
    cleaned_aids_path = "../../cleaned_data/cleaned_aids.json"
    aids = {aid["user_id"]: aid for aid in load_json(cleaned_aids_path)}

    original_fittings_path = "../../data/fittings.json"
    user_type_1_path = "../../cleaned_data/user_type_1.csv"
    user_type_2_path = "../../cleaned_data/user_type_2.csv"
    user_type_1, user_type_2 = count_user_type(original_fittings_path, user_type_1_path, user_type_2_path)

    important_params_type_1_path = "../../cleaned_data/important_params_type_1.csv"
    with open(important_params_type_1_path, "r") as file:
        reader = csv.reader(file)
        important_params_type_1 = list(line[0] for line in reader)

    important_params_type_2_path = "../../cleaned_data/important_params_type_2.csv"
    with open(important_params_type_2_path, "r") as file:
        reader = csv.reader(file)
        important_params_type_2 = list(line[0] for line in reader)

    cleaned_fittings_type_1_path = "../../cleaned_data/cleaned_fittings_type_1.json"
    cleaned_fittings_type_2_path = "../../cleaned_data/cleaned_fittings_type_2.json"
    clean_fittings(
        original_fittings_path,
        cleaned_fittings_type_1_path,
        cleaned_fittings_type_2_path,
        user_type_1,
        user_type_2,
        important_params_type_1,
        important_params_type_2,
    )

    product_type_1_path = "../../cleaned_data/product_type_1.csv"
    product_type_2_path = "../../cleaned_data/product_type_2.csv"
    count_product_type(user_type_1, user_type_2, aids, product_type_1_path, product_type_2_path)
    print(f"Time taken: {time.time() - start}s")


def clean_fittings(
    original_path,
    cleaned_fittings_type_1_path,
    cleaned_fittings_type_2_path,
    user_type_1,
    user_type_2,
    important_params_type_1,
    important_params_type_2,
):
    with open(original_path, "r") as file:
        fittings = {str(fitting["user_id"]): fitting for fitting in list(ijson.items(file, "RECORDS.item"))}

    cleaned_fittings_type_1 = []
    cleaned_fittings_type_2 = []

    for user_id in user_type_1:
        if user_id in fittings:
            fitting = extract_fitting_dict(json.loads(fittings[user_id]["fitting_content"]), important_params_type_1)
            if fitting:
                cleaned_fittings_type_1.append({"user_id": user_id, "count" : len(fitting) ,"fittings": fitting})

    with open(cleaned_fittings_type_1_path, "w") as file:
        json.dump(cleaned_fittings_type_1, file, indent=4)

    for user_id in user_type_2:
        if user_id in fittings:
            fitting = extract_fitting_dict(json.loads(fittings[user_id]["fitting_content"]), important_params_type_2)
            if fitting:
                cleaned_fittings_type_2.append({"user_id": user_id, "count" : len(fitting), "fittings": fitting})

    with open(cleaned_fittings_type_2_path, "w") as file:
        json.dump(cleaned_fittings_type_2, file, indent=4)


def count_user_type(original_path, user_type_1_path, user_type_2_path):
    user_type_1 = set()
    user_type_2 = set()

    with open(original_path, "r") as file:
        fittings = {str(fitting["user_id"]): fitting for fitting in list(ijson.items(file, "RECORDS.item"))}

        for user_id, fitting in tqdm(
            fittings.items(),
            desc="Processing",
            colour="green",
        ):
            fitting_content = json.loads(fitting["fitting_content"])
            if "ParametersDouble0" in fitting_content:
                user_type_1.add(user_id)
            else:
                user_type_2.add(user_id)

    with open(user_type_1_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for user in user_type_1:
            writer.writerow([user])

    with open(user_type_2_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for user in user_type_2:
            writer.writerow([user])

    return user_type_1, user_type_2


def count_product_type(user_type_1, user_type_2, aids, product_type_1_path, product_type_2_path):
    product_type_1 = set()
    for user_id in user_type_1:
        if str(user_id) in aids:
            product_type_1.add(aids[str(user_id)]["product_name"])
    with open(product_type_1_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for product in product_type_1:
            writer.writerow([product])

    product_type_2 = set()
    for user_id in user_type_2:
        if str(user_id) in aids:
            product_type_2.add(aids[str(user_id)]["product_name"])
    with open(product_type_2_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for product in product_type_2:
            writer.writerow([product])


def extract_fitting_dict(fitting, important_params):
    result = {}
    for key, values in fitting.items():
        for param, value in values.items():
            new_param = f"{key}_{param}"
            if new_param in important_params:
                result[new_param] = value
    if len(result) == len(important_params):
        return result
    return None


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


if __name__ == "__main__":
    main()
