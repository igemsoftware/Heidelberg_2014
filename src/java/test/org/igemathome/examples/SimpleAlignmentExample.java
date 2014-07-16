package org.igemathome.examples;

/**
 * Created by artjom on 7/16/14.
 */
public class SimpleAlignmentExample {

    public static void main(String[] args) {
        int r = SmithWaterman.align("acctg", "ccatg");
        System.out.println(r);
    }

}
