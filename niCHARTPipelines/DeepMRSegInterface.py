from nipype.interfaces.base import (CommandLine, CommandLineInputSpec,
                                    TraitedSpec, traits, File)

###--------Interface--------
class DeepMRSegInferenceInputSpec(CommandLineInputSpec):
    in_file = File(exists=True, mandatory=True, argstr='--inImg %s', position=0,desc='the input image file')
    mdl_dir1 = File( mandatory=True, argstr='--mdlDir %s', position=1,desc='the input model 1')
    mdl_dir2 = File( argstr='--mdlDir %s', desc='the input model 2')
    mdl_dir3 = File( argstr='--mdlDir %s', desc='the input model 3')
    batch_size = traits.Int(argstr="--batch %d", desc="batch size: default 64")
    nJobs = traits.Int(argstr="--nJobs %d", desc="nJobs")
    out_file = File(argstr='--outImg %s', position=-1, desc='the output image')

class DeepMRSegInferenceOutputSpec(TraitedSpec):
    out_file = File(desc='the output image')
    
class DeepMRSegInference(CommandLine):
        _cmd = 'deepmrseg_test'
        input_spec = DeepMRSegInferenceInputSpec
        output_spec = DeepMRSegInferenceOutputSpec

        def _list_outputs(self):
            outputs = self.output_spec().get()
            outputs['out_file'] = self.inputs.out_file
            return outputs

