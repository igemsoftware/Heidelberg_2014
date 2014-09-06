import _modeller
from modeller import *
from modeller.automodel import *
from modeller.optimizers import conjugate_gradients, actions
from modeller.scripts import complete_pdb


def calc(configfile, atomfile, inputsequencefile, outputfile):
    #a list, where the helical residues should be
    #TODO read out configfile
    helixrange = []
    config = open(configfile, 'r')
    for line in config:
        line = line.strip()
        values = line.split(',')
        pdbname = values[0]
        proteinname = values[1]
        residuename = values[2]
        if (len(values)-3)%2 == 0:
            for helixbase in range(3, len(values)-1, 2):
                helixrange.append((int(values[helixbase]), int(values[helixbase+1])))
        else:
            raise Exception('helixranges are not divisable by 2 --> Error in configfile')

    config.close()

    modelsegments = ('FIRST:' + residuename,'LAST:' + residuename) #from where to where in the PDB, default is first to last aa
    aligncodespdb = pdbname + residuename
    alnfile = proteinname + "-" + aligncodespdb + ".ali"
    
    log.verbose()

    env = environ()

    env.libs.topology.read('${MODINSTALL9v14}/modlib/top_heav.lib')
    env.libs.parameters.read('${MODINSTALL9v14}/modlib/par.lib')

    aln = alignment(env)
    mdl = model(env, file= atomfile, model_segment=modelsegments) #the PDB file

    aln.append_model(mdl, align_codes=aligncodespdb, atom_files=atomfile)
    aln.append(file=inputsequencefile, align_codes=proteinname) #in here the sequence has been.
    aln.align2d()

    aln.write(file=alnfile, alignment_format='PIR')

    # Disable default NTER and CTER patching
    env.patch_default = False 

    class cycModel(dopehr_loopmodel):
        def special_patches(self, aln):
            # Link between last residue (-1) and first (0) to make chain cyclic:
            self.patch(residue_type="LINK",
                        residues=(self.residues[-1], self.residues[0]))
                        
                        
                        
    class RestraintsModel(cycModel):
        def special_restraints(self, aln):
            for helix in helixrange:
                self.restraints.add(secondary_structure.alpha(self.residue_range(str(helix[0]), str(helix[1]))))


    a = RestraintsModel(env, alnfile=alnfile,
                  knowns=pdbname + residuename, sequence=proteinname,
                  assess_methods=(assess.DOPE,
                                  assess.normalized_dope,
                                  assess.DOPEHR,
                                  assess.GA341))
    # generate 10 models
    a.starting_model = 1
    a.ending_model = 10


    a.library_schedule    = autosched.slow
    a.max_var_iterations  = 5000
    a.md_level            = refine.slow
    a.repeat_optimization = 5
    a.max_molpdf = 1e6
    a.final_malign3d = True

    # generate 10*5 loopmodels
    a.loop.starting_model = 1
    a.loop.ending_model   = 5

    a.loop.library_schedule    = autosched.slow
    a.loop.max_var_iterations  = 5000
    a.loop.md_level       = refine.slow
    a.loop.repeat_optimization = 5
    a.loop.max_molpdf = 1e6
    a.loop.final_malign3d = True

    a.make()

    ok_models = [x for x in a.outputs if x['failure'] is None]

    # Rank the models by Energy Score
    ok_models.sort(key=lambda a: a['molpdf'])

    # Get top model
    bestmodel = ok_models[0]

    refmodel = complete_pdb(env, bestmodel["name"])

    refmodel_atms = selection(refmodel)
    refmodel.restraints.unpick_all()
    refmodel.restraints.condense()
    refmodel.restraints.make(refmodel_atms, restraint_type='STEREO', spline_on_site=False)
    for helix in helixrange:
        refmodel.restraints.add(secondary_structure.alpha(refmodel.residue_range(str(helix[0]), str(helix[1]))))
    sel = selection(refmodel)
    thefile = open("cg_mod_out.dat", "w")
    cg_mod = conjugate_gradients()
    cg_mod.optimize(refmodel, min_atom_shift=0.0001, max_iterations=10000, actions=[actions.trace(5,thefile)])

    refmodel.write(file=outputfile)
