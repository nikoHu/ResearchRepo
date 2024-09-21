import java.io.*;
import java.util.ArrayList;

public class Main {
    // All the static Variables
    public static ArrayList<File> allJavaFiles = new ArrayList<>();
    public static Integer numFiles = 0;

    public static Integer numUniqueFiles = 0;
    public static Integer numBlankLines = 0;
    public static Integer numCodeLines = 0;
    public static Integer numCommentLines = 0;
    public static Integer numTotalLines = 0;

    //MAIN Function
    public static void main(String[] args) {
        Config.load();
        String projectPath = Config.projectPath;
        System.out.println(projectPath);
        try {
            File file = new File(projectPath);
            if (file.isFile() && isJava(file)) {
                allJavaFiles.add(file);
                numFiles = 1;
                numUniqueFiles = 1;
                calcLines();
            } else {
                calcNumOfFiles(projectPath);
                calcNumOfUniqueFiles();
                calcLines();
            }
        } catch (Exception ex) {
//            System.out.println(ex);
        }

        System.out.print(numFiles + "-" + numUniqueFiles + "-" + numBlankLines + "-" + numCommentLines + "-" + numCodeLines);

        // Write to csv
        String writePath = Config.projectPath + File.separator + Config.writeFileName;
        writeToCSV(writePath, projectPath, "Java", numFiles, numBlankLines, numCommentLines, numCodeLines);
    }

    // Write to CSV function
    public static void writeToCSV(String filePath, String projectPath, String language, int numFiles, int numBlankLines, int numCommentLines, int numCodeLines) {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filePath))) {
            // Write header
            writer.write("项目路径,语言,源文件数,空白行数,注释行数,代码行数");
            writer.newLine();
            // Write data
            writer.write(String.format("%s,%s,%d,%d,%d,%d", projectPath, language, numFiles, numBlankLines, numCommentLines, numCodeLines));
            writer.newLine();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    //All the static Functions
    public static boolean isJava(File f) {
        String fName = f.getName();
        int dotIndex = fName.lastIndexOf('.');
        if (dotIndex != -1 && dotIndex != 0) {
            String subname = fName.substring(dotIndex);
            return subname.equals(".java");
        }
        return false;
    }


    public static Integer calcNumOfFiles(String path) {
        File file = new File(path);

        try {
            int count = 0;
            for (File f : file.listFiles()) {
                if (f.isFile() && isJava(f)) {
                    count++;
                    allJavaFiles.add(f);
//                    System.out.println("Found Java file: " + f.getPath());
                }
                if (f.isDirectory()) {
//                    System.out.println("Entering directory: " + f.getPath());
                    count += calcNumOfFiles(f.getPath());
                }
            }
            numFiles = count;
            return count;
        } catch (Exception ex) {
            ex.printStackTrace();
        }
        return null;
    }


    public static Integer calcNumOfUniqueFiles() {
        try {
            for (int i = 0; i < allJavaFiles.size() - 1; i++) {
                for (int j = i + 1; j < allJavaFiles.size(); j++) {
                    if (compareFiles(allJavaFiles.get(i), allJavaFiles.get(j))) {
                        allJavaFiles.remove(j);
                    }
                }
            }
            numUniqueFiles = allJavaFiles.size();
            return allJavaFiles.size();
            //System.out.println(compareFiles(allJavaFiles.get(222), allJavaFiles.get(222)));
            //System.out.println(compareFiles(allJavaFiles.get(1), allJavaFiles.get(0)));

        } catch (Exception ex) {
            //System.out.println(ex);
        }

        return allJavaFiles.size();
    }

    public static boolean compareFiles(File f1, File f2) {
        try {
            BufferedReader fb1 = new BufferedReader(new FileReader(f1));
            BufferedReader fb2 = new BufferedReader(new FileReader(f2));
            if (f1.length() == f2.length()) {
                String tempLine1, tempLine2;
                while (!(tempLine1 = fb1.readLine()).isEmpty()) {
                    if (!(tempLine2 = fb2.readLine()).isEmpty()) {
                        if (!tempLine1.equals(tempLine2)) {
                            return false;
                        }
                    } else return false;
                }
            } else return false;
            return true;
        } catch (Exception ex) {
            //System.out.println(ex);
        }

        return false;
    }

    public static Integer calcLines() {
        for (File f : allJavaFiles) {
            try {
                BufferedReader fb = new BufferedReader(new FileReader(f));
                String tempLine = "";
                boolean flag = false;
                while (fb != null && (tempLine = fb.readLine()) != null) {
                    numTotalLines++;
                    if (tempLine.trim().startsWith("/*") && flag == false) {
                        flag = true;
                    }
                    if (flag) {
                        numCommentLines++;
                    }
                    if (flag == false) {
                        if (tempLine.isBlank())
                            numBlankLines++;
                        if (tempLine.trim().startsWith("//"))
                            numCommentLines++;
                        if (!tempLine.isBlank() && !tempLine.trim().startsWith("//"))
                            numCodeLines++;
                    }
                    if (tempLine.contains("*/") && flag == true) {
                        flag = false;
                    }


                }
                fb.close();
            } catch (Exception ex) {
                //System.out.println(f.getName() + ex);
            }
        }
        return numBlankLines;
    }
}