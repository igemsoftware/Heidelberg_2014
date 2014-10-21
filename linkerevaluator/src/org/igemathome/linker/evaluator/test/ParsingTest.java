package org.igemathome.linker.evaluator.test;

import org.igemathome.linker.evaluator.Linker;
import org.igemathome.linker.evaluator.LinkerMotive;

/**
 * Created by Constantin on 15.09.2014.
 */
public class ParsingTest {

    public static void main(String[] args) throws Linker.LinkerParsingException {
        String linkerString = "GGHelixMotiveABCDmysuperxoolixMotivACBDHelixMBBCDHelixMotiveExtein";
        Linker linker = new Linker(Linker.aminoAcidSequenceFromString(linkerString));
        for(LinkerMotive mot : linker.getLinkerMotives()){
            System.out.println(mot);
        }
//        List<String> angleMotives = Arrays.asList("ABCD", "ACBD", "BBCD");
//        List<String> exteinMotives = Arrays.asList("Extein");
//
//        Pattern anglePatterns = Pattern.compile("GG|" + join(angleMotives, "|") + "|" + join(exteinMotives, "|"));
//        Matcher matcher = anglePatterns.matcher(linker);
//
//        boolean first = true;
//        int helixBeginn = -1;
//        while(matcher.find()){
//            if(!first){
//                System.out.println("Helix: " + linker.substring(helixBeginn,  matcher.start()));
//            }
//            System.out.print(matcher.group());
//            if("GG".equals(matcher.group())){
//                System.out.println(" is Beginning GG");
//
//            }else if(angleMotives.contains(matcher.group())){
//                System.out.println(" is Angle Motiv");
//            }else if(exteinMotives.contains(matcher.group())){
//                System.out.println(" is Extein");
//            }else{
//                throw new Linker.LinkerParsingExcepetion("Regex: " + matcher.group() +
//                        ", but non of the motives were matched");
//            }
//            helixBeginn = matcher.end();
//            first = false;
//        }
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

}
