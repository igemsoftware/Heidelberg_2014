package org.igemathome.linker.evaluator;

import org.biojava.bio.structure.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Created by Constantin on 14.09.2014.
 */
public class Linker {

    private List<AminoAcid> aminoAcidSeq;

    private List<LinkerMotive> linkerMotives;

    private static final List<String> angleMotives = new ArrayList<String>(Arrays.asList("NVL", "KTA", "AADGTL",
            "VNLTA", "AAAHPEA", "ASLPAA",
            "ATGDLA", "AASGAA", "AALAA",
            "AAWAA", "ASNA", "ASA",
            "AGA", "VV"));
    private static final List<String> exteinMotives = new ArrayList<String>(Arrays.asList("RGKCWE", "RGTCWE"));

    public Linker(List<AminoAcid> aalist) throws LinkerParsingException {

        aminoAcidSeq = aalist;
        linkerMotives = parseLinker(aalist);
        for (LinkerMotive lm : linkerMotives){
            if(lm instanceof FlexibleRegion){
                ((FlexibleRegion)lm).calculateAngles();
            }
        }
    }

    private List<LinkerMotive> parseLinker(List<AminoAcid> seq) throws LinkerParsingException {
        List<LinkerMotive> motives = new ArrayList<LinkerMotive>();

        Pattern anglePatterns = Pattern.compile("GG|" + join(angleMotives, "|") + "|" + join(exteinMotives, "|"));
        StringBuilder sb = new StringBuilder();
        for (AminoAcid aa : seq){
            sb.append(aa.getAminoType());
        }

        String sseq = sb.toString();
        System.out.println(sseq);
        Matcher matcher = anglePatterns.matcher(sseq);

        boolean first = true;
        int helixBeginn = 0;
        while(matcher.find()) {
            final String match = matcher.group();
            if (first && "GG".equals(match)){
                LinkerMotive ggMotive = new LinkerMotive(seq.subList(matcher.start(), matcher.end()), this) {
                    public String toString() {
                        return "GG: length(" + length + ")";
                    }
                };
                motives.add(ggMotive);
            }else{
                motives.add(new Helix(seq.subList(helixBeginn, matcher.start()), this));
                if(angleMotives.contains(match)){
                    motives.add(new FlexibleRegion(seq.subList(matcher.start(), matcher.end()), this));
                }else if(exteinMotives.contains(match)){
                    motives.add(new LinkerMotive(seq.subList(matcher.start(), matcher.end()), this) {
                        @Override
                        public String toString() {
                            return "Extein: length(" + length + "), seq(" + getAASeqString() + ")";
                        }
                    });
                }else{
                    throw new LinkerParsingException("Regex: " + match +
                            ", but non of the motives were matched");
                }
            }
            first = false;
            helixBeginn = matcher.end();

        }

        return motives;

    }


    public static List<AminoAcid> aminoAcidSequenceFromString(String s){
        List<AminoAcid> aaseq = new ArrayList<AminoAcid>();
        for(char c : s.toCharArray()){
            AminoAcid aa = new AminoAcidImpl();
            aa.setAminoType(c);
            aaseq.add(aa);
        }
        return aaseq;
    }

    private static String join(Iterable<String> iter, String connection){
        StringBuilder sb = new StringBuilder();
        boolean first = true;
        for (String s : iter){
            if(first){
                sb.append(s);
                first = false;
            }else{
                sb.append(connection + s);
            }
        }
        return sb.toString();
    }
    public List<LinkerMotive> getLinkerMotives() {
        return linkerMotives;
    }

    public static class LinkerParsingException extends Exception {
        public LinkerParsingException() {
        }

        public LinkerParsingException(String message) {
            super(message);
        }

        public LinkerParsingException(String message, Throwable cause) {
            super(message, cause);
        }

        public LinkerParsingException(Throwable cause) {
            super(cause);
        }
    }

}
