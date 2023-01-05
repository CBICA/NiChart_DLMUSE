import SimpleITK as sitk
import imageio

###---------mask image-----------
def apply_mask(input_image_path, input_mask_path, masked_image_filename):
    image = imageio.read_image(input_image_path)
    mask = imageio.read_image(input_mask_path)

    maskfilter = sitk.MaskImageFilter()
    maskedoutput = maskfilter.Execute(image,mask)

    imageio.write_image(maskedoutput,masked_image_filename)

