import csv as _csv

import pandas as pd
import SimpleITK as sitk

from niCHARTPipelines import ImageIO

###---------calculate ROI volumes-----------
def calculate_volume(maskfile, mapcsv, scanID, output_file):
    img = ImageIO.read_image(maskfile)

    stats = sitk.LabelShapeStatisticsImageFilter()
    stats.Execute(img)

    DerivedROIs = []
    DerivedVols = []
    ROIlist = []
    Vollist = []
    with open(mapcsv) as mapcsvfile:
        reader = _csv.reader(mapcsvfile, delimiter=',')

        # Read each line in the csv map files
        for row in reader:
            row = list(filter(lambda a: a != '', row))
            # Append the ROI number to the list
            DerivedROIs.append(row[0])
            roiInds = [int(x) for x in row[2:]]
            DerivedVols.append(sum(stats.GetPhysicalSize(l) for l in roiInds))

    #create dataframe and write it to csv
    df_MuseROIs = pd.DataFrame({'ID': DerivedROIs, scanID:DerivedVols})
    df_MuseROIs.to_csv(output_file,encoding='utf-8', index=False)

