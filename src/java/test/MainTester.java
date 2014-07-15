import org.igemathome.boinc.wrapper.BoincAPIWrapper;

import java.io.*;

public class MainTester {

    public static void main(String[] args) throws IOException {
        BoincAPIWrapper.init();
		System.out.println("Callied BoincAPIWrapper.init()");

        String initDataString = BoincAPIWrapper.getInitData().toString();
        String inputText = readFile("input.txt");

        PrintWriter out = new PrintWriter("out.txt");
        out.println(inputText);
        out.println(initDataString);
        out.println("We successfully created this super cool file");

        try {
            Thread.sleep(5000);
		} catch(InterruptedException ex) {
		    Thread.currentThread().interrupt();
		}
				System.out.println("Calling BoincAPIWrapper.finish(0)");
		BoincAPIWrapper.finish(0);
	}

    private static String readFile(String filename) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(filename));
        String everything = "";
        try {
            StringBuilder sb = new StringBuilder();
            String line = br.readLine();
            while (line != null) {
                sb.append(line);
                sb.append(System.lineSeparator());
                line = br.readLine();
            }
            everything = sb.toString();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            br.close();
        }
        return everything;
    }

}
