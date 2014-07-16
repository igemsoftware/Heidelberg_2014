package org.igemathome.examples;


/**
 * Created by artjom on 7/16/14.
 */
public class SimpleAlignmentExample {

    public static void main(String[] args) {
        SmithWaterman sw = new SmithWaterman("Hello", "Heello");
        System.out.println(sw.bestAlign());
    }

}
