# Parser 使用说明

该项目用于分析每个克隆的详细信息，包括以下内容：

- **File Path**: 文件路径
- **File Name**: 文件名
- **Callable Name**: 可调用名称
- **Parameters**: 参数
- **Type**: 类型
- **Class Name**: 类名
- **Super Class Name**: 超类名
- **Package Name**: 包名
- **Is Override**: 是否重写

## 使用方法

### 方法一：直接在 Main 中指定输入输出

1. 在 `Main.java` 中指定输入 CSV 文件路径和输出 CSV 文件路径。
2. 运行`Main.java`。
3. 结果将输出到指定的输出文件中。

### 方法二：使用 JAR 包方式

1. 将项目打包为 JAR 文件。
2. 使用命令行运行 JAR 文件，指定输入和输出路径：
   ```bash
   java -jar your-parser.jar your-path/input.csv your-path/result.csv
   ```
3. 结果将输出到指定的输出文件中。
