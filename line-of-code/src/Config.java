import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Properties;


@SuppressWarnings("ALL")
public class Config {
    public static String projectPath = "";
    public static String writeFileName = "";

    private static Properties properties = new Properties();
    public static final String CONFIG_FILE = "resources/LineOfCode.properties";
    private static final String COMMENT = "";

    /**
     * 保存配置
     */
    public static void save()throws IOException{
        properties.setProperty("projectPath", projectPath);
        properties.setProperty("writeFileName", writeFileName);
        properties.store(new FileWriter(CONFIG_FILE), COMMENT);
    }

    /**
     * 加载配置
     */
    public static void load(){
        try {
            if (new File(CONFIG_FILE).exists()){
                properties.load(new FileReader(CONFIG_FILE));
                projectPath = properties.getProperty("projectPath");
                writeFileName = properties.getProperty("writeFileName");
            }else{
                save();
                System.out.println("请修改配置文件" + CONFIG_FILE +  "！");
                System.exit(0);
            }
        } catch (Exception e) {
            System.out.println("配置文件读取异常");
            e.printStackTrace();
        }
    }

    public static Properties getProperties() {
        return properties;
    }
}
