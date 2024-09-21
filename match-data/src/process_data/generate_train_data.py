import json
import time

from sklearn.model_selection import train_test_split


def main():
    start = time.time()
    cleaned_users_path = "../../cleaned_data/cleaned_users.json"
    cleaned_aids_path = "../../cleaned_data/cleaned_aids.json"
    cleaned_audiograms_path = "../../cleaned_data/cleaned_audiograms.json"
    cleaned_fittings_type_1_path = "../../cleaned_data/cleaned_fittings_type_1.json"
    cleaned_fittings_type_2_path = "../../cleaned_data/cleaned_fittings_type_2.json"

    data_path_1 = "../../train_data/type_1/data.json"
    train_data_path_1 = "../../train_data/type_1/train.json"
    valid_data_path_1 = "../../train_data/type_1/valid.json"
    test_data_path_1 = "../../train_data/type_1/test.json"

    data_path_2 = "../../train_data/type_2/data.json"
    train_data_path_2 = "../../train_data/type_2/train.json"
    valid_data_path_2 = "../../train_data/type_2/valid.json"
    test_data_path_2 = "../../train_data/type_2/test.json"

    generate_train_data(
        cleaned_users_path,
        cleaned_aids_path,
        cleaned_audiograms_path,
        cleaned_fittings_type_1_path,
        data_path_1,
        train_data_path_1,
        valid_data_path_1,
        test_data_path_1,
    )
    # generate_train_data(
    #     cleaned_users_path,
    #     cleaned_aids_path,
    #     cleaned_audiograms_path,
    #     cleaned_fittings_type_2_path,
    #     data_path_2,
    #     train_data_path_2,
    #     valid_data_path_2,
    #     test_data_path_2,
    # )
    print(f"Time: {time.time() - start}")


def generate_train_data(
    users_path, aids_path, audiograms_path, fittins_path, data_path, train_data_path, valid_data_path, test_data_path
):
    users = load_json(users_path)
    aids = {aid["user_id"]: aid for aid in load_json(aids_path)}
    audiograms = {audiogram["user_id"]: audiogram for audiogram in load_json(audiograms_path)}
    fittings = {fitting["user_id"]: fitting for fitting in load_json(fittins_path)}

    merged_datas = []
    for user in users:
        merged_item = user.copy()
        user_id = user["user_id"]
        if user_id in aids and user_id in audiograms and user_id in fittings:
            merged_datas.append(merged_item | aids[user_id] | audiograms[user_id] | fittings[user_id])

    new_merged_datas = []
    for i, merged_data in enumerate(merged_datas):
        user_info = {
            "age": merged_data["age"],
        }

        audiograms = merged_data["audiograms"]
        for key, value in audiograms.items():
            user_info[key] = value

        new_merged_datas.append(
            {
                "id": i + 1,
                "user_id": merged_data["user_id"],
                "count": len(merged_data["fittings"]),
                "user_info": user_info,
                "parameter": merged_data["fittings"],
            }
        )

    with open(data_path, "w") as file:
        json.dump(new_merged_datas, file, indent=4)

    # train_data, remain_data = train_test_split(new_merged_datas, test_size=0.2, random_state=42)
    # valid_data, test_data = train_test_split(remain_data, test_size=0.5, random_state=42)

    # for data, path in zip([train_data, valid_data, test_data], [train_data_path, valid_data_path, test_data_path]):
    #     with open(path, "w") as file:
    #         json.dump(data, file, indent=4)


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


if __name__ == "__main__":
    main()
