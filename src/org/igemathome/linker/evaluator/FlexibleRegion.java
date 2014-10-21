package org.igemathome.linker.evaluator;

import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.biojava.bio.structure.AminoAcid;

import java.util.List;

/**
 * Created by Constantin on 14.09.2014.
 */
public class FlexibleRegion extends LinkerMotive{


    private double angleHH;

    private double angleHF;

    private double angleFH;
    private boolean hasCalculatedAngles;

    public FlexibleRegion(List<AminoAcid> aaseq, Linker linker) throws Linker.LinkerParsingException {
        super(aaseq, linker);
    }

    public void calculateAngles() {
        try {
            hasCalculatedAngles = true;
            Helix nHelix = (Helix) previous();
            Helix cHelix = (Helix) next();
            angleHH = Vector3D.angle(nHelix.getDirectionVector(), cHelix.getDirectionVector());
            angleHF = Vector3D.angle(nHelix.getDirectionVector(), endPoint.subtract(startPoint));
            angleFH = Vector3D.angle(endPoint.subtract(startPoint), cHelix.getDirectionVector());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    public String toString() {
        if(hasCalculatedAngles)
            return "FlexRegion: length(" + length + "), seq(" + getAASeqString() + "), angle(" + angleHH + ", " + angleHF + ", " + angleFH + ")";
        else
            return "FlexRegion: length(" + length + "), seq(" + getAASeqString() + "), angle(" + angleHH + ")";
    }

    /**
     * The angle between previous Helix and Flexibel region (estimated as direct connection between 2 Helices)
     * @return
     */
    public double getAngleHF() {
        return angleHF;
    }

    /**
     * The angle between Flexibel region (estimated as direct connection between 2 Helices) and next helix
     * @return
     */
    public double getAngleFH() {
        return angleFH;
    }
}
