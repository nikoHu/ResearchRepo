import json
import glob
import re
from opencc import OpenCC
from tqdm import tqdm

# 初始化 OpenCC 转换器
cc = OpenCC('t2s')  # 繁体到简体

# 获取所有 poet.song.xx.json 文件
json_files = glob.glob('../chinese-poetry/全唐诗/poet.song.*.json')

# 输出文件
output_file = 'dataset.txt'

# 计算总诗歌数量
total_poems = 0
for file in json_files:
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        total_poems += len(data)

def is_valid_poem(poem):
    # 检查是否为单句诗
    if len(poem) == 1 and poem[0].endswith('。'):
        return False
    
    # 检查是否包含中文逗号句号之外的符号
    pattern = re.compile(r'[^\u4e00-\u9fa5，。]')
    for line in poem:
        if pattern.search(line):
            return False
    
    # 检查是否所有句子都能被中文逗号分割且长度大于1
    for line in poem:
        if len(line.split('，')) == 1:
            return False
    
    return True

with open(output_file, 'w', encoding='utf-8') as out_f:
    # 创建绿色进度条
    pbar = tqdm(total=total_poems, colour='green', desc="处理进度")
    
    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for poem in data:
                # 获取 paragraphs 并转换为简体
                paragraphs = [cc.convert(p) for p in poem['paragraphs']]
                # 跳过包含无法显示字符的段落
                if any('□' in p for p in paragraphs):
                    pbar.update(1)
                    continue
                # 检查是否为有效诗歌
                if not is_valid_poem(paragraphs):
                    pbar.update(1)
                    continue
                # 将 paragraphs 写入文件，用空格连接
                out_f.write(' '.join(paragraphs) + '\n')
                # 更新进度条
                pbar.update(1)
    
    # 关闭进度条
    pbar.close()

print(f"处理完成，结果已保存到 {output_file}")