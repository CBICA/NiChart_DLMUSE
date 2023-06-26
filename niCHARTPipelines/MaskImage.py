import SimpleITK as sitk

from niCHARTPipelines import ImageIO


###---------mask image-----------
def apply_mask(input_image_path, input_mask_path, masked_image_filename):
    image = ImageIO.read_image(input_image_path)
    mask = ImageIO.read_image(input_mask_path)

    maskfilter = sitk.MaskImageFilter()
    maskedoutput = maskfilter.Execute(image,mask)

    ImageIO.write_image(maskedoutput,masked_image_filename)

