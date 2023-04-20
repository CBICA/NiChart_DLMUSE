from nipype.interfaces.base import (CommandLine, CommandLineInputSpec,
                                    TraitedSpec, traits, Directory)

###--------Interface--------
class nnUNetInferenceInputSpec(CommandLineInputSpec):
    in_dir = Directory(exists=True, mandatory=True, argstr='--i %s', position=0,desc='the input folder')
    mdl_dir = Directory( mandatory=True, argstr='--mdlDir %s', position=1,desc='the input model')
    f_val = traits.Int( mandatory=True,argstr='-f %d', desc="f val: default 0")
    t_val = traits.Int(mandatory=True,argstr='-t %d', desc="t val: default 803")
    # batch_size = traits.Int(argstr="--batch %d", desc="batch size: default 64")
    m_val = traits.Str(mandatory=True,argstr='-m %s',desc="m val: default 3d_fullres")
    gpu_val = traits.Str(mandatory=True,argstr='--all_in_gpu %s',desc="gpu val: default True")
    out_dir = Directory(argstr='-o %s', position=-1, desc='the output folder')

class nnUNetInferenceOutputSpec(TraitedSpec):
    out_dir = Directory(desc='the output folder')
    
class nnUNetInference(CommandLine):
        _cmd = 'nnUNet_predict'
        input_spec = nnUNetInferenceInputSpec
        output_spec = nnUNetInferenceOutputSpec

        def _list_outputs(self):
            outputs = self.output_spec().get()
            outputs['out_dir'] = self.inputs.out_file
            return outputs

