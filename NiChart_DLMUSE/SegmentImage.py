import os
import glob
import shutil

def run_dlicv(in_dir, in_suff, out_dir, out_suff, device):
    '''
    '''
    
    # Call DLICV
    print('Running DLICV')
    os.system(f'DLICV -i {in_dir} -o {out_dir} -device {device}')

    print('Rename dlicv out file')    
    for fname in glob.glob(os.path.join(out_dir, "label_*.nii.gz")):
        new_fname = fname.replace("label_", "", 1).replace(in_suff, out_suff)
        #os.rename(fname, new_fname)
        #shutil.copyfile(fname, new_fname)
        print(fname)
        print(new_fname)
        

def run_dlmuse(in_dir, in_suff, out_dir, out_suff, device):
    '''
    '''
    
    # Call DLMUSE
    print('Running DLMUSE')
    os.system(f'DLMUSE -i {in_dir} -o {out_dir} -device {device}')

    print('Rename dlmuse out file')    
    for fname in glob.glob(os.path.join(out_dir, "DLMUSE_mask_*.nii.gz")):
        new_fname = fname.replace("DLMUSE_mask_", "", 1).replace(in_suff, out_suff)
        #os.rename(fname, new_fname)
        shutil.copyfile(fname, new_fname)
        print(fname)
        print(new_fname)
