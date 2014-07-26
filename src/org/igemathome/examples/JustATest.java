package org.igemathome.examples;

/**
 * Created by artjom on 7/17/14.
 */
public class JustATest {

    public static void main(String[] args) {
        System.out.println("Hello");
        SmithWaterman sm = new SmithWaterman("Computer", "Computation");
        System.out.println(sm.bestAlign());
    }

}
