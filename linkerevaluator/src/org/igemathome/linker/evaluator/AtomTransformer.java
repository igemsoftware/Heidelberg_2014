package org.igemathome.linker.evaluator;

import org.biojava.bio.structure.Atom;
import org.biojava.bio.structure.AtomImpl;
import org.biojava.bio.structure.Calc;
import org.biojava.bio.structure.jama.Matrix;

/**
 * Created by Constantin on 24.09.2014.
 */
public class AtomTransformer {

    private Matrix rotMatrix;
    private Atom shiftVector;
    private double alignScore;

    public AtomTransformer(Matrix rotMatrix, Atom shiftVector, double alignScore){
        this.rotMatrix = rotMatrix;
        this.shiftVector = shiftVector;
        this.alignScore = alignScore;
    }

    public AtomTransformer(Matrix rotMatrix, Atom shiftVector){
        this(rotMatrix, shiftVector, -1);
    }

    public Atom transform(Atom a){
        Atom r = (Atom)a.clone();
        Calc.rotate(r, rotMatrix);
        Calc.shift(r, shiftVector);
        return r;
    }

}
