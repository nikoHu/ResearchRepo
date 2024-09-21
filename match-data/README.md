# 助听器参数预测

本项目旨在基于病人的基本信息和测听数据预测助听器的参数。该任务是一个多输出回归问题，项目中实现了多种方法来完成这个目标。最后我们发现使用简单的深度学习和基于Transformer做多输出回归的效果最好，准确率能达到**99%**。

## 目录
- [安装](#安装)
- [使用](#使用)
- [方法](#方法)
- [数据处理](#数据处理)
- [模型](#模型)

## 安装

项目使用 `pdm` 进行管理。如果尚未安装，可以通过 `pip` 进行安装：

```sh
pip install pdm
```

安装 `pdm` 后，克隆此仓库并安装项目依赖：

```sh
git clone https://github.com/yourusername/hearing-aid-parameter-prediction.git
cd hearing-aid-parameter-prediction
pdm install
```

## 使用

你可以运行位于 `src/methods` 目录中的不同方法来训练模型。请确保首先运行 `src/process_data` 目录中的脚本来处理你的数据。例如：
```sh
pdm run generate_train_data.py
```

## 方法

本项目中实现了以下方法：

- **BERT**：
  - 文件：`src/methods/Bert.ipynb`
  - 描述：使用 BERT 模型预训练进行回归。

- **深度学习**：
  - 文件：`src/methods/Deep Learning.ipynb`
  - 描述：使用深度学习方法进行预测。

- **随机森林**：
  - 文件：`src/methods/Random Forest.ipynb`
  - 描述：使用随机森林算法。

- **Transformer 分类**：
  - 文件：`src/methods/Transformer_classification.ipynb`
  - 描述：使用 Transformer 模型进行分类任务。

- **Transformer 回归**：
  - 文件：`src/methods/Transformer_regression.ipynb`
  - 描述：使用 Transformer 模型进行回归任务。

## 数据处理

以下脚本用于数据处理：

- **clean_input_data.py**：
  - 描述：清理输入数据的脚本。
  - 文件：`src/process_data/clean_input_data.py`

- **clean_output_data.py**：
  - 描述：清理输出数据的脚本。
  - 文件：`src/process_data/clean_output_data.py`

- **diff_important_params.py**：
  - 描述：查找重要参数差异的脚本。
  - 文件：`src/process_data/diff_important_params.py`

- **generate_train_data.py**：
  - 描述：生成训练数据的脚本。
  - 文件：`src/process_data/generate_train_data.py`

## 模型

训练好的模型存储在 `src/models` 目录中。因为参数有两种类型，所以分别训练了模型，包括：

- Transformer for Regression
  - `best_model_type_1.pth`
  - `best_model_type_2.pth`
- Transformer for classification
  - `transformer_60.pth`
  - `transformer_80.pth`
  - `transformer_100.pth`
  - `transformer_120.pth`
  - `transformer_type_2_40.pth`
  - `transformer_type_2_60.pth`
  - `transformer_type_2_80.pth`
- Deep learning
  - `dl_model_type_1.pth`
- Random forest
  - `rf_model_type_1.pkl`
