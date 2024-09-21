package com.parser;

import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.InitializerDeclaration;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.CSVRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;
import java.util.stream.Collectors;

public class Main {
    private static final Logger logger = LoggerFactory.getLogger(Main.class);

    public static void main(String[] args) {
        String inputCsvPath = args.length >= 1 ? args[0] : "data/input.csv";
        String outputCsvPath = args.length >= 2 ? args[1] : "data/result.csv";

        try {
            processAndWriteFunctionsRealTime(inputCsvPath, outputCsvPath);
            logger.info("处理完成，结果已写入 {}", outputCsvPath);
        } catch (IOException e) {
            logger.error("处理过程中发生错误", e);
        }
    }

    private static void processAndWriteFunctionsRealTime(String inputCsvPath, String outputCsvPath) throws IOException {
        CSVFormat csvFormat = CSVFormat.DEFAULT.builder()
                .setHeader("ID", "File Path", "File Name", "Callable Name", "Parameters", "Type", "Class Name", "Super Class Name", "Package Name", "Is Override")
                .build();

        ParserConfiguration config = new ParserConfiguration();
        config.setLanguageLevel(ParserConfiguration.LanguageLevel.JAVA_21);
        StaticJavaParser.setConfiguration(config);

        try (BufferedReader reader = Files.newBufferedReader(Paths.get(inputCsvPath), StandardCharsets.UTF_8);
             CSVParser parser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader());
             CSVPrinter printer = new CSVPrinter(new OutputStreamWriter(new FileOutputStream(outputCsvPath), StandardCharsets.UTF_8), csvFormat)) {

            long totalRecords = Files.lines(Paths.get(inputCsvPath)).count() - 1; // Subtract 1 for header
            long processedRecords = 0;

            for (CSVRecord record : parser) {
                String id = record.get(0);
                String originalFilePath = record.get(1);

                // Add error handling for parsing integers
                int startLine, endLine;
                try {
                    startLine = Integer.parseInt(record.get(2).trim());
                    endLine = Integer.parseInt(record.get(3).trim());
                } catch (NumberFormatException e) {
                    logger.warn("Invalid line numbers for ID={}, File={}: startLine='{}', endLine='{}'",
                            id, originalFilePath, record.get(2), record.get(3));
                    continue;  // Skip this record and move to the next one
                }

                Path path = Paths.get(originalFilePath);
                String fileName = path.getFileName().toString();

                try {
                    CompilationUnit cu = StaticJavaParser.parse(path);
                    Optional<FunctionInfo> functionInfoOpt = findTargetCallable(cu, id, originalFilePath, fileName, startLine, endLine);
                    if (functionInfoOpt.isPresent()) {
                        FunctionInfo info = functionInfoOpt.get();
                        printer.printRecord(info.id, info.filePath, info.fileName, info.callableName, info.parameters, info.type, info.className, info.superClassName, info.packageName, info.isOverride);
                        printer.flush(); // 确保数据被写入文件
                    } else {
                        logger.warn("未找到匹配的方法、构造函数或静态初始化块: ID={}, 文件={}, 开始行={}, 结束行={}", id, originalFilePath, startLine, endLine);
                    }
                } catch (com.github.javaparser.ParseProblemException e) {
                    logger.warn("存在语法问题，无法匹配: ID={}, 文件={}, 开始行={}, 结束行={}", id, originalFilePath, startLine, endLine);
                    logger.debug("详细错误信息: ", e);
                } catch (Exception e) {
                    logger.error("读取或解析文件时发生错误: {}", originalFilePath, e);
                }

                processedRecords++;
                int progress = (int) ((processedRecords * 100) / totalRecords);
                System.out.print(String.format("\r处理进度: %3d%%\t", progress));
            }
            System.out.println();
        }
    }

    private static Optional<FunctionInfo> findTargetCallable(CompilationUnit cu, String id, String filePath, String fileName, int startLine, int endLine) {
        String packageName = cu.getPackageDeclaration().map(pd -> pd.getNameAsString()).orElse("");

        Optional<MethodDeclaration> methodOpt = cu.findAll(MethodDeclaration.class).stream()
                .filter(m -> isInRange(m, startLine, endLine))
                .findFirst();

        if (methodOpt.isPresent()) {
            MethodDeclaration method = methodOpt.get();
            ClassInfo classInfo = getClassInfo(method);
            boolean isOverride = method.getAnnotationByName("Override").isPresent();
            return Optional.of(new FunctionInfo(id, filePath, fileName, method.getNameAsString(), method.getParameters().toString(), "Method", classInfo.className, classInfo.superClassName, packageName, isOverride));
        }

        Optional<ConstructorDeclaration> constructorOpt = cu.findAll(ConstructorDeclaration.class).stream()
                .filter(c -> isInRange(c, startLine, endLine))
                .findFirst();

        if (constructorOpt.isPresent()) {
            ConstructorDeclaration constructor = constructorOpt.get();
            ClassInfo classInfo = getClassInfo(constructor);
            return Optional.of(new FunctionInfo(id, filePath, fileName, constructor.getNameAsString(), constructor.getParameters().toString(), "Constructor", classInfo.className, classInfo.superClassName, packageName, false));
        }

        Optional<InitializerDeclaration> initializerOpt = cu.findAll(InitializerDeclaration.class).stream()
                .filter(i -> isInRange(i, startLine, endLine))
                .findFirst();

        if (initializerOpt.isPresent()) {
            InitializerDeclaration initializer = initializerOpt.get();
            String type = initializer.isStatic() ? "Static Initializer" : "Instance Initializer";
            ClassInfo classInfo = getClassInfo(initializer);
            return Optional.of(new FunctionInfo(id, filePath, fileName, "", "", type, classInfo.className, classInfo.superClassName, packageName, false));
        }

        return Optional.empty();
    }

    private static boolean isInRange(com.github.javaparser.ast.Node node, int startLine, int endLine) {
        return node.getBegin().isPresent() && node.getEnd().isPresent() &&
                ((node.getBegin().get().line <= startLine && node.getEnd().get().line >= endLine) ||
                        (node.getBegin().get().line >= startLine && node.getBegin().get().line <= endLine));
    }

    private static ClassInfo getClassInfo(com.github.javaparser.ast.Node node) {
        Optional<ClassOrInterfaceDeclaration> classOpt = node.findAncestor(ClassOrInterfaceDeclaration.class);
        if (classOpt.isPresent()) {
            ClassOrInterfaceDeclaration classDeclaration = classOpt.get();
            String className = classDeclaration.getNameAsString();
            String superClassName = classDeclaration.getExtendedTypes().stream()
                    .map(t -> t.getNameAsString())
                    .collect(Collectors.joining(", "));
            return new ClassInfo(className, superClassName);
        }
        return new ClassInfo("", "");
    }

    private static class FunctionInfo {
        String id;
        String filePath;
        String fileName;
        String callableName;
        String parameters;
        String type;
        String className;
        String superClassName;
        String packageName;
        boolean isOverride;

        FunctionInfo(String id, String filePath, String fileName, String callableName, String parameters, String type, String className, String superClassName, String packageName, boolean isOverride) {
            this.id = id;
            this.filePath = filePath;
            this.fileName = fileName;
            this.callableName = callableName;
            this.parameters = parameters;
            this.type = type;
            this.className = className;
            this.superClassName = superClassName;
            this.packageName = packageName;
            this.isOverride = isOverride;
        }
    }

    private static class ClassInfo {
        String className;
        String superClassName;

        ClassInfo(String className, String superClassName) {
            this.className = className;
            this.superClassName = superClassName;
        }
    }
}