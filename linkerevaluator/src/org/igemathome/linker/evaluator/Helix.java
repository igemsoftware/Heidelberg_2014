package org.igemathome.linker.evaluator;

import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.biojava.bio.structure.AminoAcid;
import org.biojava.bio.structure.StructureException;

import java.util.List;

/**
 * Created by Constantin on 14.09.2014.
 */
public class Helix extends LinkerMotive{

////---------------------Static Elements-------------------------------------------------------------------------------//
//
//    public static List<String> helixMotives = new ArrayList<String>();
//    static{
//        helixMotives.add("AEAAK");
//    }

//-------------------------------------------------------------------------------------------------------------------//


    private Vector3D directionVector;

    public Helix(List<AminoAcid> aaseq, Linker linker) throws Linker.LinkerParsingException {
        super(aaseq, linker);
        try {
            directionVector = new Vector3D(aaseq.get(0).getCA().getCoords()).subtract(
                    new Vector3D(aaseq.get(aaseq.size()-1).getCA().getCoords()));

        } catch (StructureException e) {
            throw new IllegalArgumentException(e);
        }
    }

    @Override
    public String toString() {
        return "Helix: length("+ length + "), seq(" + getAASeqString() + ")";
    }

    public Vector3D getDirectionVector() {
        return directionVector;
    }
}
