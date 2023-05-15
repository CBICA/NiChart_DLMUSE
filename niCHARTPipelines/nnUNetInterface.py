from nipype.interfaces.base import (CommandLine, CommandLineInputSpec,
                                    TraitedSpec, traits, Directory)
import os
###--------Interface--------
class nnUNetInferenceInputSpec(CommandLineInputSpec):
    in_dir = Directory(mandatory=True,argstr='-i %s', position=0,desc='the input folder')
    f_val = traits.Int( argstr='-f %d', desc="f val: default 0")
    t_val = traits.Int(argstr='-t %d', desc="t val: default 803")
    m_val = traits.Str(argstr='-m %s',desc="m val: default 3d_fullres")
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

