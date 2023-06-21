docker run --rm -v $(pwd)/temp/nnUNet_raw_data_base/nnUNet_raw_data:/input \
                -v$(pwd)/temp/nnUNet_out:/output:rw \
                -v$(pwd)/temp/:/mappings \
                -v$(pwd)/temp/nnUNet_model:/models \
                -it aidinisg/nichartpipelines:0.1.4 niCHARTPipelines -i /input/ \
                                                                     -o /output \
                                                                     -p structural \
                                                                     -s 123 \
                                                                     --derived_ROI_mappings_file /mappings/MUSE_mapping_derived_rois.csv \
                                                                     --MUSE_ROI_mappings_file /mappings/MUSE_mapping_consecutive_indices.csv \
                                                                     --results_folder /models \ 
                                                                     --all_in_gpu False



sudo docker run -v $(pwd)/temp/nnUNet_raw_data_base/nnUNet_raw_data:/input \
           -v$(pwd)/temp/nnUNet_out:/output:rw \
           -v$(pwd)/temp/:/mappings \
           -v$(pwd)/temp/nnUNet_model:/models \
           test niCHARTPipelines -i /input/ \
                                 -o /output \
                                 -p structural \
                                 -s 123 \
                                 --derived_ROI_mappings_file /mappings/MUSE_mapping_derived_rois.csv \
                                 --MUSE_ROI_mappings_file /mappings/MUSE_mapping_consecutive_indices.csv \
                                 --results_folder /models \ 
                                 --all_in_gpu False