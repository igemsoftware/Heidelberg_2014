package org.igemathome.linker.evaluator;

import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.biojava.bio.structure.AminoAcid;

import java.util.List;

/**
 * Created by Constantin on 14.09.2014.
 */
public abstract class LinkerMotive {

    protected Vector3D startPoint;
    protected Vector3D endPoint;
    protected List<AminoAcid> aminoAcidSeq;
    private Linker linker;

    protected double length;

    public LinkerMotive(List<AminoAcid> aaseq, Linker linker) throws Linker.LinkerParsingException {
        aminoAcidSeq = aaseq;
        this.linker = linker;
        try {
            startPoint = new Vector3D(aaseq.get(0).getCA().getCoords());
            endPoint = new Vector3D(aaseq.get(aaseq.size()-1).getCA().getCoords());
            length = endPoint.subtract(startPoint).getNorm();
        } catch (Exception e) {
            e.printStackTrace();
            throw new Linker.LinkerParsingException(this + " (Illegal Linker Motive): " + aaseq);
        }
    }

    public String getAASeqString() {
        StringBuilder sb = new StringBuilder();
        for (AminoAcid aa : aminoAcidSeq) {
            sb.append(aa.getAminoType());
        }
        return sb.toString();
    }

    public LinkerMotive previous(){
        int index = linker.getLinkerMotives().indexOf(this);
        return  index <= 0 ? null : linker.getLinkerMotives().get(index-1);
    }

    public LinkerMotive next(){
        int index = linker.getLinkerMotives().indexOf(this);
        return  index == linker.getLinkerMotives().size()-1 ? null : linker.getLinkerMotives().get(index+1);
    }

}