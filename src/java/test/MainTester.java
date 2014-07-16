import org.igemathome.boinc.wrapper.BoincAPIWrapper;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

public class MainTester {

    public static void main(String[] args) throws IOException {
        BoincAPIWrapper.init();
        System.out.println("Called BoincAPIWrapper.init()");

        String initDataString = BoincAPIWrapper.getInitData().toString();
        String inputText = readFile(BoincAPIWrapper.boinc_resolve_filename_s("input.txt"));

        try {
            Path file = Files.createFile(Paths.get(BoincAPIWrapper.boinc_resolve_filename_s("out.txt")));
            Files.write(file, "I'm a text and this is cool".getBytes(), StandardOpenOption.CREATE);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            Thread.sleep(5000);
		} catch(InterruptedException ex) {
		    Thread.currentThread().interrupt();
		}

        System.out.println("Calling BoincAPIWrapper.finish(0)");
        BoincAPIWrapper.finish(0);
	}

    private static String readFile(String filename) throws IOException {
        String everything = "";
        try {
            Path p = Paths.get(filename);
            everything = new String(Files.readAllBytes(p), StandardCharsets.UTF_8);
        } catch (IOException ex) {
            ex.printStackTrace();
        }

        return everything;
    }

}
