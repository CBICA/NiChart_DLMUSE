import SimpleITK as sitk

###----image read/write
def read_image(input_file_path):
    reader = sitk.ImageFileReader()
    reader.SetFileName ( str(input_file_path) )
    image = reader.Execute()
    return image

def write_image(output, output_file_path):
    writer = sitk.ImageFileWriter()
    writer.SetFileName ( str(output_file_path) )
    writer.Execute ( output )
