import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

/**
 * Created by artjom on 7/16/14.
 */
public class IOPractise {

    public static void main(String[] args) {
        System.out.println("Hello IOPractise");
        FileSystem fs = FileSystems.getDefault();


        Path p = fs.getPath("src", "java", "test", "out.txt");
        try {
            Path file = Files.createFile(p);
            Files.write(p, "I'm a text and this is cool".getBytes(), StandardOpenOption.CREATE);
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            System.out.println(p.toRealPath(LinkOption.NOFOLLOW_LINKS));
            System.out.println(new String(Files.readAllBytes(p), StandardCharsets.UTF_8));
        } catch (IOException ex) {
            ex.printStackTrace();
        }

        try {
            boolean deleted = Files.deleteIfExists(p);
            System.out.println("Deleted file: " + p + ": " + deleted);
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

}
