package org.igemathome.examples;

/**
 * Created by artjom on 7/16/14.
 */
public class SmithWaterman {

    private int[][] matrix;

    private String result;

    public SmithWaterman(String seq1, String seq2) {
        prepareMatrix(seq1.length(), seq2.length());
        fillMatrix(seq1, seq2);
        System.out.println(printMatrix());

        result = backtrace(seq1, seq2);
    }

    private String backtrace(String seq1, String seq2) {
        int highest = 0;
        int[] highestLoc = {0, 0};
        for (int a = 1; a < matrix.length; a++) {
            for (int b = 1; b < matrix[a].length; b++) {
                if (matrix[a][b] >= highest) {
                    highestLoc[0] = a;
                    highestLoc[1] = b;
                    highest = matrix[a][b];
                }
            }
        }
        System.out.println(highestLoc[0] + ", " + highestLoc[1]);
        StringBuilder sb = new StringBuilder();
        for (int a = highestLoc[0]; a > 0; ) {
            for (int b = highestLoc[1]; b > 0; ) {
                int[] nextLoc;
                if (matrix[a - 1][b - 1] >= matrix[a - 1][b] && matrix[a - 1][b - 1] >= matrix[a][b - 1]) {
                    nextLoc = new int[]{-1, -1};
                    sb.append(seq1.charAt(a - 1));
                } else if (matrix[a - 1][b] >= matrix[a][b - 1]) {
                    nextLoc = new int[]{-1, 0};
                    sb.append("");
                } else {
                    nextLoc = new int[]{0, -1};
                    sb.append("-");
                }
                a = a + nextLoc[0];
                b = b + nextLoc[1];
                System.out.println("Reading: [" + a + "," + b + "]");
            }
        }

        return sb.reverse().toString();
    }


    private void fillMatrix(String seq1, String seq2) {
        for (int a = 1; a < matrix.length; a++) {
            for (int b = 1; b < matrix[a].length; b++) {
                int value = (seq1.charAt(a - 1) == seq2.charAt(b - 1) ? 1 : -1) + matrix[a - 1][b - 1];
                matrix[a][b] = value < 0 ? 0 : value;
            }
        }
    }

    private void prepareMatrix(int length1, int length2) {
        matrix = new int[length1 + 1][length2 + 1];
//        for (int a = 0; a <= length1; a++) {
//            matrix[a][0] = a;
//        }
//        for (int b = 0; b <= length1; b++) {
//            matrix[0][b] = b;
//        }
    }


    public String printMatrix() {
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

    public int[][] getMatrix() {
        return matrix;
    }

}
