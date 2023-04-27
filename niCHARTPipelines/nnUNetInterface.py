from nipype.interfaces.base import (CommandLine, CommandLineInputSpec,
                                    TraitedSpec, traits, Directory)
import os
###--------Interface--------
class nnUNetInferenceInputSpec(CommandLineInputSpec):
    in_dir = Directory(mandatory=True,argstr='-i %s', position=0,desc='the input folder')
    #mdl_dir = Directory( argstr='%s',desc='the input model')
    f_val = traits.Int( argstr='-f %d', desc="f val: default 0")
    t_val = traits.Int(argstr='-t %d', desc="t val: default 803")
    m_val = traits.Str(argstr='-m %s',desc="m val: default 3d_fullres")
    #gpu_val = traits.Str(argstr='--all_in_gpu %s',desc="gpu val: default True")
    out_dir = Directory(mandatory=True,argstr='-o %s', position=-1, desc='the output folder')

class nnUNetInferenceOutputSpec(TraitedSpec):
    out_dir = Directory(desc='the output folder')
    
class nnUNetInference(CommandLine):
        _cmd = 'nnUNet_predict'
        input_spec = nnUNetInferenceInputSpec
        output_spec = nnUNetInferenceOutputSpec

        def _list_outputs(self):
            outputs = self.output_spec().get()
            outputs['out_dir'] = self.inputs.out_dir
            return outputs

#muse = nnUNetInference()
#muse.inputs.in_dir = '/niCHARTPipelines/sharedFolder/Data/'
##model_loc = '/niCHARTPipelines/sharedFolder/Model/'
##os.environ['RESULTS_FOLDER'] = model_loc
##mdl_dir = '/niCHARTPipelines/sharedFolder/DLMUSE_Model/'
#mdl_dir = '/niCHARTPipelines/sharedFolder/Model'
#os.environ['RESULTS_FOLDER'] = mdl_dir
#muse.inputs.f_val = 0
#muse.inputs.t_val = 803
#muse.inputs.m_val = "3d_fullres"
##muse.gpu_val = True
#muse.inputs.out_dir = '/niCHARTPipelines/sharedFolder/Results2'
#r = muse.run()