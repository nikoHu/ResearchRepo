import csv
import json
import time
import re


def main():
    start = time.time()
    original_users_path = "../../data/users.json"
    cleaned_users_path = "../../cleaned_data/cleaned_users.json"
    clean_users(original_users_path, cleaned_users_path)

    original_aids_path = "../../data/aids.json"
    cleaned_aids_path = "../../cleaned_data/cleaned_aids.json"
    count_unique_products_path = "../../cleaned_data/count_unique_products.csv"
    clean_aids(original_aids_path, cleaned_aids_path, count_unique_products_path)

    original_audiograms_path = "../../data/audiograms.json"
    cleaned_audiograms_path = "../../cleaned_data/cleaned_audiograms.json"
    clean_audiograms(original_audiograms_path, cleaned_audiograms_path)
    print(f"Time: {time.time() - start}")


def clean_users(original_path, cleaned_path):
    users = {user["user_idcard"]: user for user in load_json(original_path)["RECORDS"]}
    cleaned_user = []  # 17220
    count = 1
    for _, user in users.items():
        user_id = user["user_id"]
        created_time = user["created_time"]
        user_birthday = user["user_birthday"]
        if created_time and user_birthday:
            age = int(created_time.split("-")[0]) - int(user_birthday.split("-")[0])
            if 0 < age <= 150:
                cleaned_user.append(
                    {
                        "id": count,
                        "user_id": user_id,
                        "age": age,
                    },
                )
                count += 1
    with open(cleaned_path, "w") as file:
        json.dump(cleaned_user, file, indent=4)


def clean_aids(original_path, cleaned_path, count_unique_products_path):
    aids = {str(aid["user_id"]): aid for aid in load_json(original_path)["RECORDS"]}
    cleaned_aids = []  # 23572
    count_products = set()
    for user_id, aid in aids.items():
        product_name = aid["product_name"].strip("*")
        count_products.add(product_name)
        if user_id and product_name and not re.search(r"[\u4e00-\u9fff]", product_name):
            cleaned_aids.append(
                {
                    "user_id": user_id,
                    "product_id": str(aid["aid_id"]),
                    "product_name": product_name,
                },
            )

    with open(cleaned_path, "w") as file:
        json.dump(cleaned_aids, file, indent=4)

    with open(count_unique_products_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "product_name"])
        for i, product in enumerate(count_products):
            if not re.search(r"[\u4e00-\u9fff]", product):
                writer.writerow([i + 1, product])


def clean_audiograms(original_path, cleaned_path):
    audiograms = {str(audiogram["user_id"]): audiogram for audiogram in load_json(original_path)["RECORDS"]}
    cleaned_audiograms = []  # 23684
    for user_id, audiogram in audiograms.items():
        audiogram_content = json.loads(audiogram["audiogram_content"])
        if user_id and audiogram_content:
            audiogram_right = clean_ear_audiograms(audiogram_content["AudiogramRight"], "r")
            audiogram_left = clean_ear_audiograms(audiogram_content["AudiogramLeft"], "l")
            if audiogram_right and audiogram_left and len(audiogram_right) + len(audiogram_left) == 60:
                cleaned_audiograms.append(
                    {
                        "user_id": user_id,
                        "audiograms": {
                            **audiogram_right,
                            **audiogram_left,
                        },
                    }
                )

    with open(cleaned_path, "w") as file:
        json.dump(cleaned_audiograms, file, indent=4)


def clean_ear_audiograms(audiogram, ear):
    result = {}
    for key, values in audiogram.items():
        for freq, value in values.items():
            result[f"{ear}_{key.lower()}_{freq}"] = value
    return result


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


if __name__ == "__main__":
    main()
