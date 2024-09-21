import re

def clean_poem(poem):
    # 去除所有的空格
    poem = poem.replace(" ", "")
    return poem.strip()

def extract_first_5w_lines(input_file, output_file, num_lines=20200):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            with open(output_file, 'w', encoding='utf-8') as outfile:
                for _ in range(num_lines):
                    line = infile.readline()
                    if not line:
                        break
                    line = clean_poem(line)
                    outfile.write(line + '\n')  # 添加换行符，确保每行诗句单独一行
        print(f"Successfully extracted the first {num_lines} lines to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

input_file = 'dataset.txt'
output_file = 'poetry.txt'
extract_first_5w_lines(input_file, output_file)