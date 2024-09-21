```markdown
# Crawler

## 简介
这一个用于从 GitHub 上抓取开源项目的工具。它可以根据特定的关键词和条件，收集项目的相关信息，并将其保存为 CSV 文件。

## 功能
- 根据关键词和星级范围搜索 GitHub 项目
- 支持 API 限制处理
- 下载项目的压缩包
- 保存抓取的项目数据到 CSV 文件
- 进度保存和恢复功能

## 安装
确保你已经安装了 Python 3.x 和相关依赖库。可以使用以下命令安装所需的库：

```bash
pip install requests
```

## 使用方法
1. 在 `main.py` 中设置你的 GitHub 访问令牌。
2. 配置代理（如果需要）。
3. 运行 `main.py` 来开始抓取项目。

```bash
python crawler/main.py
```

## 配置
在 `main.py` 中，你可以修改以下内容：
- `keywords`：定义要搜索的关键词。
- `categories`：设置要抓取的项目类别及目标数量。