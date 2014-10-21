package org.igemathome.linker.evaluator;

import org.biojava.bio.structure.*;
import org.biojava.bio.structure.align.StructureAlignment;
import org.biojava.bio.structure.align.StructureAlignmentFactory;
import org.biojava.bio.structure.align.fatcat.FatCatRigid;
import org.biojava.bio.structure.align.fatcat.calc.FatCatParameters;
import org.biojava.bio.structure.align.model.AFPChain;
import org.biojava.bio.structure.io.PDBFileReader;
import org.biojava3.core.sequence.io.util.IOUtils;
import org.igemathome.wrapper.BoincAPIWrapper;
import java.io.*;
import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/**
 * Created by Constantin on 12.09.2014.
 */
public class Main {



    public static void main(String[] args) throws IOException {

        BoincAPIWrapper.init();

        String resolveOutFilename = BoincAPIWrapper.resolveFilename("out.txt");
        String resolveInFilename = BoincAPIWrapper.resolveFilename("pdbs.zip");

        PrintStream stream = new PrintStream(new File(resolveOutFilename));
        System.setOut(stream);
        System.setErr(stream);
        PDBFileReader pdbReader = new PDBFileReader();

//        pdbReader.getStructure()

        String source = args.length == 0 ? resolveInFilename : args[0];
        ZipFile zf = new ZipFile(source);

        File refTmpFile = null;
        out: for (ZipEntry entry : Collections.list(zf.entries())) {
            if(entry.getName().toLowerCase().equals("master.pdb")){
                refTmpFile = stream2file(zf.getInputStream(entry));
                break out;
            }
        }

        if (refTmpFile == null) {
            System.err.println("Failed to find master.pdb");
            BoincAPIWrapper.finish(1);
        }

        loop:
        for (ZipEntry linkerEntry : Collections.list(zf.entries())) {
            if (!linkerEntry.isDirectory() && !linkerEntry.getName().toLowerCase().equals("master.pdb")) {
                try {

                    System.out.println("-----------------------------------------------");

                   // ZipEntry linkerEntry = findMatchingLinkerEntry(entry.getName(), zf);
                    File linkerTmpFile = stream2file(zf.getInputStream(linkerEntry));
                    System.out.println("Results for: " + linkerEntry.getName());

                    Chain reference = pdbReader.getStructure(refTmpFile).getChain(0);
                    Chain calcProt = pdbReader.getStructure(linkerTmpFile).getChain(0);

                    List<AminoAcid> linkerAA = extractLinker(reference, calcProt);
                    AtomTransformer transformer = alignStructures(reference, calcProt);
                    try {
                        Linker linker = new Linker(linkerAA);
                        for (LinkerMotive m : linker.getLinkerMotives()) {
                            System.out.print(m);
                            if (m instanceof Helix) {
                                Atom firstCA = m.aminoAcidSeq.get(0).getCA();
                                System.out.print(", firstCA (" + Arrays.toString(transformer.transform(firstCA).getCoords()) + ")");
                                Atom lastCA = m.aminoAcidSeq.get(m.aminoAcidSeq.size() - 1).getCA();
                                System.out.print(", lastCA (" + Arrays.toString(transformer.transform(lastCA).getCoords()) + ")");
                            }
                            System.out.println();
                        }
                    } catch (Linker.LinkerParsingException linkerParsingException) {
                        linkerParsingException.printStackTrace();
                    } catch (StructureException e) {
                        e.printStackTrace();
                    }
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            } catch (Exception e) {
                e.printStackTrace();
            }
            System.out.println("-----------------------------------------------");
        }
    }

    System.out.flush();
    BoincAPIWrapper.finish(0);
}

//    private static ZipEntry findMatchingLinkerEntry(String name, ZipFile zf) {
//        for(ZipEntry entry : Collections.list(zf.entries())){
//            if(!entry.getName().equals(name) && entry.getName().toLowerCase().contains(name.substring(0, 4).toLowerCase())){
//                return entry;
//            }
//        }
//
//        return null;
//    }

    public static File stream2file (InputStream in) throws IOException {
        final File tempFile = File.createTempFile(nextRandomFileName(), ".pdb");
        tempFile.deleteOnExit();
        try (FileOutputStream out = new FileOutputStream(tempFile)) {
            IOUtils.copy(in, out);
        }
        return tempFile;
    }

//    public static File stream2dir (InputStream in) throws IOException {
//        final File  tempDir = Files.createTempDirectory(Paths.get("."), "").toFile();
//        tempDir.deleteOnExit();
//        try (FileOutputStream out = new FileOutputStream(tempDir)) {
//            IOUtils.copy(in, out);
//        }
//        return tempDir;
//    }


    private static List<AminoAcid> extractLinker(Chain reference, Chain calcProt) throws Linker.LinkerParsingException {
        List<AminoAcid> ar = convertGroupToAminoAcids(reference.getAtomGroups("amino"));
        List<AminoAcid> ac = convertGroupToAminoAcids(calcProt.getAtomGroups("amino"));
        int beginnOfLinker = ar.get(ar.size()-1).getResidueNumber().getSeqNum()+1;
        if (beginnOfLinker > ac.size()) {
            System.out.println("Failed to find linker. Forgot to add it");
            throw new Linker.LinkerParsingException("Beginn of Linker is after end of protein. Please check structure");
        }
        List<AminoAcid> linker = ac.subList(beginnOfLinker, ac.size());

        // sublist only retunrs a view on the original object!!
        return new ArrayList<AminoAcid>(linker);
    }

    private static List<AminoAcid> convertGroupToAminoAcids(List<Group> log){
        try {
            List<AminoAcid> loa = new ArrayList<AminoAcid>();
            for (Group g : log) {
                loa.add((AminoAcid) g);
            }
            return loa;
        }catch(ClassCastException ex){
            throw new IllegalArgumentException("List must only contain Aminoacids");
        }
    }

    /**
     *
     * @param c1 Reference Chain
     * @param c2 Transformed Chain
     */
    private static AtomTransformer alignStructures(Chain c1, Chain c2) {
        try {
            final Atom[] ca1 = StructureTools.getAtomCAArray(c1);
            final Atom[] ca2 = StructureTools.getAtomCAArray(c2);

            StructureAlignment algorithm  =  StructureAlignmentFactory.getAlgorithm(FatCatRigid.algorithmName);
            FatCatParameters params = new FatCatParameters();


            final AFPChain afpChain = algorithm.align(ca1,ca2,params);
            System.out.println("AlignScore: " + afpChain.getAlignScore());
            return new AtomTransformer(afpChain.getBlockRotationMatrix()[afpChain.getBlockNum()-1],
                    afpChain.getBlockShiftVector()[afpChain.getBlockNum()-1], afpChain.getAlignScore());

        } catch (StructureException e) {
            e.printStackTrace();
            return null;
        }
    }

private static SecureRandom random = new SecureRandom();

    public static String nextRandomFileName() {
        return new BigInteger(130, random).toString(32);
    }

//    private static void alignStructures(Chain c1, Chain c2) {
//        try {
//
//
//
//            final Atom[] ca1 = StructureTools.getAtomCAArray(c1);
//            final Atom[] ca2 = StructureTools.getAtomCAArray(c2);
//
//            StructureAlignment algorithm  =  StructureAlignmentFactory.getAlgorithm(FatCatRigid.algorithmName);
//            FatCatParameters params = new FatCatParameters();
//
//
//            final AFPChain afpChain = algorithm.align(ca1,ca2,params);
//
//            afpChain.setName1("Reference");
//            afpChain.setName2("Linker");
//
//            System.out.println(afpChain.toRotMat());
//
//
//
//            System.out.println(afpChain.getAlignScore());
//
//            new Thread(new Runnable() {
//                @Override
//                public void run() {
//                    try {
//                        StructureAlignmentDisplay.display(afpChain, ca1, ca2);
//                    } catch (StructureException e) {
//                        e.printStackTrace();
//                    }
//                }
//            }).start();
//
//
//        } catch (StructureException e) {
//            e.printStackTrace();
//        }
//    }

}
