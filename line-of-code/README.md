# LineOfCode

## 简介
LineOfCode 是一个用于统计 Java 项目代码行数的工具。它可以计算源文件数、空白行数、注释行数和代码行数，并将结果输出到 CSV 文件中。您也可以直接使用 [cloc](https://github.com/AlDanial/cloc) 这个开源工具来完成相同的任务。

## 功能
- 读取指定项目路径下的 Java 文件
- 统计代码行数、空白行数和注释行数
- 将统计结果写入 CSV 文件

## 使用方法
1. 修改 `resources/LineOfCode.properties` 文件，设置 `projectPath` 和 `writeFileName`。
2. 运行 `Main.java` 文件。
3. 结果将输出到指定的 CSV 文件中。
