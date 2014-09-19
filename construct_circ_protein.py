from modeller import *
from modeller.automodel import *
from modeller.optimizers import conjugate_gradients, actions
from modeller.scripts import complete_pdb
from modeller.util.logger import *
import loader


def calc(version, configfile, atomfile, inputsequencefile, outputfile):
    #a list, where the helical residues should be
    #TODO read out configfile
    try:
        global log
        helixrange = []
        config = open(configfile, 'r')
        for line in config:
            line = line.strip()
            values = line.split(',')
            pdbname = values[0]
            proteinname = values[1]
            residuename = values[2]
            startlinker = values[3]
            endlinker   = values[4]
            if (len(values)-3)%2 == 0:
                for helixbase in range(3, len(values)-1, 2):
                    helixrange.append((int(values[helixbase]), int(values[helixbase+1])))
            else:
                log.error("calc", "wrong number of parameters in configfile")
                config.close()
                return -2
        config.close()
    except:
        log.error("calc", "reading config file")
        return -3

    try:
        modelsegments = ('FIRST:' + residuename,'LAST:' + residuename) #from where to where in the PDB, default is first to last aa
        aligncodespdb = pdbname + residuename
        alnfile = proteinname + "-" + aligncodespdb + ".ali"

        log.minimal()
        env = environ()

        env.libs.topology.read('${MODINSTALL9v14}/modlib/top_heav.lib')
        env.libs.parameters.read('${MODINSTALL9v14}/modlib/par.lib')
    except:
        log.error("calc", "unable to setup environment")
        return -4

    try:
        aln = alignment(env)
        mdl = model(env, file= atomfile, model_segment=modelsegments) #the PDB file

        aln.append_model(mdl, align_codes=aligncodespdb, atom_files=atomfile)
        aln.append(file=inputsequencefile, align_codes=proteinname) #in here the sequence has been.
        aln.align2d()

        aln.write(file=alnfile, alignment_format='PIR')
    except:
        log.error("calc", "unable to write alignment file")
        return -5

    class cycModel(dopehr_loopmodel):
        def special_patches(self, aln):
            # Link between last residue (-1) and first (0) to make chain cyclic:
            self.patch(residue_type="LINK",
                        residues=(self.residues[-1], self.residues[0]))
                        
                        
                        
    class RestraintsModel(cycModel):
        def special_restraints(self, aln):
            for helix in helixrange:
                self.restraints.add(secondary_structure.alpha(self.residue_range(str(helix[0]), str(helix[1]))))

    class MyLoop(RestraintsModel):
        def select_loop_atoms(self):
            return selection(self.residue_range(startlinker, endlinker))


    # Disable default NTER and CTER patching
    env.patch_default = False 

       
    try:
        a = MyLoop(env, alnfile=alnfile,
                      knowns=pdbname + residuename, sequence=proteinname,
                      loop_assess_methods=(assess.DOPE,
                                      assess.normalized_dope,
                                      assess.DOPEHR,
                                      assess.GA341))
        # generate 10 models
        a.starting_model = 1
        a.ending_model = 1


        a.library_schedule    = autosched.slow
        a.max_var_iterations  = 5000
        a.md_level            = refine.slow
        a.repeat_optimization = 5
        a.max_molpdf = 1e6
        a.final_malign3d = True
        
        # generate 10*5 loopmodels
        a.loop.starting_model = 1
        a.loop.ending_model   = 1

        a.loop.library_schedule    = autosched.slow
        a.loop.max_var_iterations  = 5000
        a.loop.md_level       = refine.slow
        a.loop.repeat_optimization = 5
        a.loop.max_molpdf = 1e6
        a.loop.final_malign3d = True
    except:
        log.error("calc", "setting up loopmodal")
        return -6

    try:
        a.make()
    except:
        log.error("calc", "making loopmodal")
        return -7

    try:
        ok_models = [x for x in a.loop.outputs if x['failure'] is None]

        # Rank the models by Energy Score
        ok_models.sort(key=lambda a: a['DOPE-HR score'])

        # Get top model
        bestmodel = ok_models[0]

        loader.log( "BEGIN***************************************************************************")
        loader.log( str(bestmodel['DOPE-HR score']) + ";" + str(bestmodel['Normalized DOPE score']))
        loader.log( "END*****************************************************************************")
    except:
        log.error("calc", "find best model")
        return -8
        
    try:

        refmodel = complete_pdb(env, bestmodel["name"])

        refmodel_atms = selection(refmodel)
        refmodel.restraints.unpick_all()
        refmodel.restraints.condense()
    except:
        log.error("calc", "refmodel started")
        return -8
    
    

    try:
        refmodel.restraints.make(refmodel_atms, restraint_type='STEREO', spline_on_site=False)
    except:
        log.error("calc", "making refmodal")
        return -9

    try:
        for helix in helixrange:
            refmodel.restraints.add(secondary_structure.alpha(refmodel.residue_range(str(helix[0]), str(helix[1]))))
        sel = selection(refmodel)
    except:
        log.error("calc", "adding helixranges to restraints")
        return -10

    try:
        thefile = open("cg_mod_out.dat", "w")
    except:
        log.error("calc", "opening file cg_mod_out.dat")
        return -11
    
    try:
        cg_mod = conjugate_gradients()
        cg_mod.optimize(refmodel, min_atom_shift=0.0001, max_iterations=10000, actions=[actions.trace(5,thefile)])
    except:
        log.error("calc", "cg_mod.optimize")
        return -12

    try:
        refmodel.write(file=outputfile)
    except:
        log.error("calc", "writing outputfile %s" % outputfile)
        return -13

    return 0
