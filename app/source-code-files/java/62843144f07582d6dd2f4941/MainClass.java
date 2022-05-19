import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.commons.cli.HelpFormatter;

public class MainClass
{
    static String ARRAY_SPLIT = ",";
    
    static int add(int a,int b){
	return a+b
}

    public static int parse_integer(String sArg){
        return Integer.parseInt(sArg);
    }

    public static float parse_float(String sArg){
        return Float.parseFloat(sArg);
    }

    public static boolean parse_boolean(String sArg){
        return Boolean.parseBoolean(sArg);
    }

    public static String parse_String(String sArg){
        return sArg;
    }

    public static int[] parse_array_integer_(String sArg){
        String[] parts = sArg.split(ARRAY_SPLIT);
        int[] array = new int[parts.length];
        for (int i = 0; i < parts.length; i++)
            array[i] = Integer.parseInt(parts[i]);
        return array;
    }

    public static float[] parse_array_float_(String sArg){
        String[] parts = sArg.split(ARRAY_SPLIT);
        float[] array = new float[parts.length];
        for (int i = 0; i < parts.length; i++)
            array[i] = Float.parseFloat(parts[i]);
        return array;
    }

    public static boolean[] parse_array_boolean_(String sArg){
        String[] parts = sArg.split(ARRAY_SPLIT);
        boolean[] array = new boolean[parts.length];
        for (int i = 0; i < parts.length; i++)
            array[i] = Boolean.parseBoolean(parts[i]);
        return array;
    }

    public static String[] parse_array_string_(String sArg){
        return sArg.split(ARRAY_SPLIT);
    }


    public static void main(String args[]) {
        Options options = new Options();
        options.addOption("a", true, "Enter this required argument");
	options.addOption("b", true, "Enter this required argument");

        HelpFormatter formatter = new HelpFormatter();
        CommandLineParser parser = new DefaultParser();
        CommandLine cmd;

        try {
            cmd = parser.parse(options, args);
        } catch (ParseException e) {
            System.out.println(e.getMessage());
            formatter.printHelp("User Profile Info", options);
            System.exit(1);
            return;
        }
        
        String arg_a = cmd.getOptionValue("a");
	String arg_b = cmd.getOptionValue("b");

        int input_a = parse_integer(arg_a);
	int input_b = parse_integer(arg_b);

        Object result;
        result = add(input_a,input_b);
 	

        System.out.println(result);
            


        

    }
}