package org.igemathome.examples;

/**
 * Created by artjom on 7/16/14.
 */
public class SmithWaterman {

    private int[][] matrix;

    private String result;

    public SmithWaterman(String seq1, String seq2) {
        prepareMatrix(seq1.length(), seq2.length());
        System.out.println(printMatrix());
    }

    private void prepareMatrix(int length1, int length2) {
        matrix = new int[length1 + 1][length2 + 1];
        for (int a = 0; a <= length1; a++) {
            matrix[a][0] = a;
        }
        for (int b = 0; b <= length1; b++) {
            matrix[b][0] = b;
        }
    }

    private String printMatrix() {
        if (matrix == null) {
            return "[]";
        } else {
            StringBuilder sb = new StringBuilder();
            for (int a = 0; a < matrix.length; a++) {
                for (int b = 0; b < matrix[a].length; b++) {
                    sb.append(matrix[a][b]);
                }
                sb.append("\n");
            }
            return sb.toString();
        }
    }


    public String bestAlign() {
        return result;
    }

}
