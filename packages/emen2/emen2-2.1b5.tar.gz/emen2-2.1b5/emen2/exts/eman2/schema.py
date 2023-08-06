import os
import json
import sys

# ParamDefs for EMData
# This Python file is encoding:UTF-8 Encoded
	
paramdefs = [
{
	'desc_short': 'Host endian-ness',
	'name': 'emdata_hostendian',
	'vartype': 'string'
}, {
	'desc_short': 'Angstroms per pixel (X)',
	'name': 'emdata_apix_x',
	'vartype': 'float',
	'property': 'length',
	'defaultunits': 'Angstrom'
}, {
	'desc_short': 'Angstroms per pixel (Y)',
	'name': 'emdata_apix_y',
	'vartype': 'float',
	'property': 'length',
	'defaultunits': 'Angstrom'
}, {
	'desc_short': 'Angstroms per pixel (Z)',
	'name': 'emdata_apix_z',
	'vartype': 'float',
	'property': 'length',
	'defaultunits': 'Angstrom'
}, {
	'desc_long': 'An integer which is incremented every time the image is marked as changed',
	'desc_short': 'Change count',
	'name': 'emdata_changecount',
	'vartype': 'int'
}, {
	'desc_long': 'Set by classification routines to indicate which class number the particle is in',
	'desc_short': 'Class ID',
	'name': 'emdata_class_id',
	'vartype': 'int'
}, {
	'desc_long': 'In a class-average, this is a list of particle numbers used in the final average (see class_ptcl_src and exc_class_ptcl_idxs)',
	'desc_short': 'Particles',
	'iter': True,
	'name': 'emdata_class_ptcl_idxs',
	'vartype': 'int'
}, {
	'desc_long': 'In a class-average, this is the file containing the raw images used to create the average',
	'desc_short': 'Particle source',
	'name': 'emdata_class_ptcl_src',
	'vartype': 'string'
}, {
	'desc_long': 'Set to true if the CTF phases have been flipped',
	'desc_short': 'CTF phase flipped',
	'name': 'emdata_ctf_phase_flipped',
	'vartype': 'boolean'
}, {
	'desc_long': 'Set in class-averages by some averagers indicating the total estimated radial SNR of the average',
	'desc_short': 'CTF total SNR',
	'iter': True,
	'name': 'emdata_ctf_snr_total',
	'vartype': 'float'
}, {
	'desc_long': 'Set to true if a Wiener filter has been applied',
	'desc_short': 'CTF Weiner filtered',
	'name': 'emdata_ctf_wiener_filtered',
	'vartype': 'boolean'
}, {
	'desc_long': 'Used in virtual stacks. This is the image number',
	'desc_short': 'Image number',
	'name': 'emdata_data_n',
	'vartype': 'int'
}, {
	'desc_long': 'Used only in BDB files, to indicate that the binary data for an image should be read from an alternate location. Data cannot be written back to such objects.',
	'desc_short': 'Data path',
	'name': 'emdata_data_path',
	'vartype': 'string'
}, {
	'desc_long': 'Used in virtual stacks. This is a reference back to the source image from which this image was derived',
	'desc_short': 'Data source',
	'name': 'emdata_data_source',
	'vartype': 'string'
}, {
	'desc_long': 'Pixel storage data type in EMAN format: EM_UCHAR, EM_SHORT, EM_USHORT, EM_SHORT_COMPLEX, EM_FLOAT, EM_FLOAT_COMPLEX',
	'desc_short': 'Datatype',
	'name': 'emdata_datatype',
	'vartype': 'int'
}, {
	'desc_long': 'Eigenvalue, only set for images which represent Eigenvectors',
	'desc_short': 'Eigenvalue',
	'name': 'emdata_eigval',
	'vartype': 'float'
}, {
	'desc_long': 'In a class-average, this is a list of particle numbers provided to the averager, but excluded from the final average (see class_ptcl_src)',
	'desc_short': 'Excluded particles',
	'iter': True,
	'name': 'emdata_exc_class_ptcl_idxs',
	'vartype': 'int'
}, {
	'desc_long': 'Flag indicating that the image is complex (R/I or A/P pairs)',
	'desc_short': 'Real image (R/I or A/P pairs)',
	'name': 'emdata_is_complex',
	'vartype': 'int'
}, {
	'desc_long': 'Flag indicating that a complex image is R/I not A/P',
	'desc_short': 'Real image (not complex)',
	'name': 'emdata_is_complex_ri',
	'vartype': 'int'
}, {
	'desc_long': 'Kurtosis of the pixel values',
	'desc_short': 'Kurtosis',
	'name': 'emdata_kurtosis',
	'vartype': 'float'
}, {
	'desc_long': 'Represents the number of a reference particle this particle best matched',
	'desc_short': 'Best particle match index',
	'name': 'emdata_match_n',
	'vartype': 'int'
}, {
	'desc_long': 'used to represent the quality associated with match_n, smaller is a better match',
	'desc_short': 'Match quality',
	'name': 'emdata_match_qual',
	'vartype': 'float'
}, {
	'desc_long': 'Largest value in the image',
	'desc_short': 'Max value',
	'name': 'emdata_maximum',
	'vartype': 'float'
}, {
	'desc_long': 'The average pixel value in the image',
	'desc_short': 'Average value',
	'name': 'emdata_mean',
	'vartype': 'float'
}, {
	'desc_long': 'The mean value of all nonzero pixels',
	'desc_short': 'Mean value',
	'name': 'emdata_mean_nonzero',
	'vartype': 'float'
}, {
	'desc_long': 'Median value of the pixel values',
	'desc_short': 'Median value',
	'name': 'emdata_median',
	'vartype': 'float'
}, {
	'desc_long': 'Cs of the microscope in mm',
	'desc_short': 'Microscope Cs',
	'name': 'emdata_microscope_cs',
	'vartype': 'float',
	'property': 'length',
	'defaultunits': 'mm'
}, {
	'desc_long': 'Voltage of the microscope in kV',
	'desc_short': 'Microscope Voltage',
	'property': 'voltage',
	'defaultunits': 'kV',
	'name': 'emdata_microscope_voltage',
	'vartype': 'float'
}, {
	'desc_long': 'Smallest value in the image',
	'desc_short': 'Min value',
	'name': 'emdata_minimum',
	'vartype': 'float'
}, {
	'desc_long': 'In a projection during multi-model refinement, this is the index of the model for the current projection. For single model refinements always 0',
	'desc_short': 'Model ID',
	'name': 'emdata_model_id',
	'vartype': 'int'
}, {
	'desc_long': 'Median value of nonzero pixels',
	'desc_short': 'Median value',
	'name': 'emdata_nonzero_median',
	'vartype': 'float'
}, {
	'desc_short': 'Image size (X)',
	'name': 'emdata_nx',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_short': 'Image size (Y)',
	'name': 'emdata_ny', 
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_short': 'Image size (Z)',
	'name': 'emdata_nz', 
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_short': 'Image origin (X)', 
	'name': 'emdata_origin_x', 
	'vartype': 'float',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_short': 'Image origin (Y)', 
	'name': 'emdata_origin_y', 
	'vartype': 'float',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_short': 'Image origin (Z)',
	'name': 'emdata_origin_z', 
	'vartype': 'float',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_long': 'In a class-average, this represents the image file which was used for initial alignment references',
	'desc_short': 'Initial alignment references', 
	'name': 'emdata_projection_image',
	'vartype': 'string'
}, {
	'desc_long': 'In a class-average, this represents the specific image number in projection_image',
	'desc_short': 'Alignment reference index', 
	'name': 'emdata_projection_image_idx',
	'vartype': 'int'
}, {
	'desc_long': 'The two endpoints and a box width that defines a helix box (x1, y1, x2, y2, box_width)',
	'desc_short': 'Helical coordinates (x1, y1, x2, y2, box_width)', 
	'iter': True,
	'name': 'emdata_ptcl_helix_coords',
	'vartype': 'int'
}, {
	'desc_long': 'If an image/volume represents the combination of one or more other images, this is the count of the number of particles that went into the average',
	'desc_short': 'Particles used for average', 
	'name': 'emdata_ptcl_repr',
	'vartype': 'int'
}, {
	'desc_long': 'The central coordinate of a boxed particle in terms of its source image, normally (x,y), may be (x,y,z) for subtomograms',
	'desc_short': 'Box coordinate',
	'iter': True,
	'name': 'emdata_ptcl_source_coord',
	'vartype': 'int'
}, {
	'desc_long': 'The name of the image from which the particle was extracted. Full path, may be in bdb syntax',
	'desc_short': 'Source image', 
	'name': 'emdata_ptcl_source_image',
	'vartype': 'string'
}, {
	'desc_long': 'Normalization factor applied to a single projection/class-average during reconstruction',
	'desc_short': 'Normalization factor', 
	'name': 'emdata_reconstruct_norm',
	'vartype': 'float'
}, {
	'desc_long': 'Set if the image has been preprocessed for use with a reconstructor',
	'desc_short': 'Preprocssed for use with a reconstructor', 
	'name': 'emdata_reconstruct_preproc',
	'vartype': 'boolean'
}, {
	'desc_long': 'Quality of a single projection/class-average relative to others during reconstruction. Unlike with comparators, larger values are better.',
	'desc_short': 'Reconstruction quality', 
	'name': 'emdata_reconstruct_qual',
	'vartype': 'float'
}, {
	'desc_long': 'Used when rendering an image to 8/16 bit integers. These are the values representing the minimum and maximum integer values',
	'desc_short': 'Min rendered value', 
	'name': 'emdata_render_max',
	'vartype': 'float'
}, {
	'desc_long': 'Used when rendering an image to 8/16 bit integers. These are the values representing the minimum and maximum integer values',
	'desc_short': 'Max rendered value', 
	'name': 'emdata_render_min',
	'vartype': 'float'
}, {
	'desc_long': 'Used when a volume has been segmented into regions. Set of 3*nregions floats in x1,y1,z1,x2,y2,z2,... order, indicating the center of each region as defined by the specific algorithm',
	'desc_short': 'Segment centers', 
	'iter': True,
	'name': 'emdata_segment_centers',
	'vartype': 'float'
}, {
	'desc_long': 'The standard deviation of the pixel values in the image',
	'desc_short': 'Sigma', 
	'name': 'emdata_sigma',
	'vartype': 'float'
}, {
	'desc_long': 'The standard deviation of the pixels ignoring pixels which are zero',
	'desc_short': 'Sigma (non-zero)', 
	'name': 'emdata_sigma_nonzero',
	'vartype': 'float'
}, {
	'desc_long': 'Skewness of the pixel values',
	'desc_short': 'Skewness', 
	'name': 'emdata_skewness',
	'vartype': 'float'
}, {
	'desc_long': 'When an image is read from a file, this is set to the image number',
	'desc_short': 'Source image number', 
	'name': 'emdata_source_n',
	'vartype': 'string'
}, {
	'desc_long': 'When an image is read from a file, this is set to the filename',
	'desc_short': 'Source path', 
	'name': 'emdata_source_path',
	'vartype': 'string'
}, {
	'desc_long': 'Sum of the squares of the pixel values',
	'desc_short': 'Pixel value sum of squares', 
	'name': 'emdata_square_sum',
	'vartype': 'float'
}, {
	'desc_long': "Used with subvolume_x0,... Specifies the size of the virtual volume that 'this' is a part of",
	'desc_short': 'Subvolume size (X)', 
	'name': 'emdata_subvolume_full_nx',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_long': "Used with subvolume_y0,... Specifies the size of the virtual volume that 'this' is a part of",
	'desc_short': 'Subvolume size (Y)', 
	'name': 'emdata_subvolume_full_ny',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_long': "Used with subvolume_z0,... Specifies the size of the virtual volume that 'this' is a part of",
	'desc_short': 'Subvolume size (Z)', 
	'name': 'emdata_subvolume_full_nz',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_long': "Used when the EMData stores only a portion of a larger image in certain contexts (notably direct Fourier inversion. This represents the location of the origin of 'this' in the larger virtual volume",
	'desc_short': 'Subvolume full (X origin)', 
	'name': 'emdata_subvolume_x0',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_long': "Used when the EMData stores only a portion of a larger image in certain contexts (notably direct Fourier inversion. This represents the location of the origin of 'this' in the larger virtual volume",
	'desc_short': 'Subvolume full (Y origin)', 
	'name': 'emdata_subvolume_y0',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_long': "Used when the EMData stores only a portion of a larger image in certain contexts (notably direct Fourier inversion. This represents the location of the origin of 'this' in the larger virtual volume",
	'desc_short': 'Subvolume full (Z origin)', 
	'name': 'emdata_subvolume_z0',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_long': 'In a 3D map, this is a list of particle numbers excluded from the final map (see threed_ptcl_src) timestamp string When data for an image is being written this is updated with the current time. It is not updated for metadata changes, only when the image data is written',
	'desc_short': 'Particles excluded from 3D map',
	'iter': True,
	'name': 'emdata_threed_excl_ptcl_idxs',
	'vartype': 'int'
}, {
	'desc_long': 'In a 3D map, this is a list of particle numbers used in the final reconstruction (see threed_ptcl_src)',
	'desc_short': 'Particles used for 3D map',
	'iter': True,
	'name': 'emdata_threed_ptcl_idxs',
	'vartype': 'int'
}, {
	'desc_long': 'In a 3D map, this is the file containing the raw images used to create the reconstruction',
	'desc_short': 'Source image for particles for 3D map',
	'name': 'emdata_threed_ptcl_src',
	'vartype': 'string'
}, {
	'desc_short': '(MRC) Minimum density value',
	'name': 'mrc_minimum',
	'vartype': 'float'
}, {
	'desc_short': '(MRC) Maximum density value',
	'name': 'mrc_maximum',
	'vartype': 'float'
}, {
	'desc_short': '(MRC) Mean density value', 
	'name': 'mrc_mean', 
	'vartype': 'float'
}, {
	'desc_long': 'No. of first column in map',
	'desc_short': '(MRC) Start (Column)', 
	'name': 'mrc_nxstart',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_long': 'No. of first row in map',
	'desc_short': '(MRC) Start (Row)', 
	'name': 'mrc_nystart',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_long': 'No. of first section in map',
	'desc_short': '(MRC) Start (Section)',
	'name': 'mrc_nzstart',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_long': 'Number of intervals along X',
	'desc_short': '(MRC) Intervals (Columns)', 
	'name': 'mrc_mx',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_long': 'Number of intervals along Y',
	'desc_short': '(MRC) Intervals (Rows)',
	'name': 'mrc_my',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_long': 'Number of intervals along Z',
	'desc_short': '(MRC) Intervals (Sections)',
	'name': 'mrc_mz',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_short': '(MRC) Size (Columns)',
	'name': 'mrc_nx', 
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_short': '(MRC) Size (Rows)',
	'name': 'mrc_ny', 
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_short': '(MRC) Size (Sections)',
	'name': 'mrc_nz', 
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_short': '(MRC) Cell dimensions (Columns)',
	'name': 'mrc_xlen',
	'vartype': 'float',
	'property': 'length',
	'defaultunits': 'Angstrom'
}, {
	'desc_short': '(MRC) Cell dimensions (Rows)',
	'name': 'mrc_ylen',
	'vartype': 'float',
	'property': 'length',
	'defaultunits': 'Angstrom'
}, {
	'desc_short': '(MRC) Cell dimensions (Columns)',
	'name': 'mrc_zlen',
	'vartype': 'float',
	'property': 'length',
	'defaultunits': 'Angstrom'
}, {
	'desc_short': '(MRC) Cell angles (Alpha, in Degrees)',
	'name': 'mrc_alpha',
	'vartype': 'float'
}, {
	'desc_short': '(MRC) Cell angles (Beta, in Degrees)',
	'name': 'mrc_beta',
	'vartype': 'float'
}, {
	'desc_short': '(MRC) Cell angles (Gamma, in Degrees)',
	'name': 'mrc_gamma',
	'vartype': 'float'
}, {
	'desc_short': '(MRC) Axis for columns',
	'name': 'mrc_mapc',
	'vartype': 'int'
}, {
	'desc_short': '(MRC) Axis for rows',
	'name': 'mrc_mapr',
	'vartype': 'int'
}, {
	'desc_short': '(MRC) Axis for setions',
	'name': 'mrc_maps',
	'vartype': 'int'
}, {
	'desc_long': 'Space group number (0 for images)',
	'desc_short': '(MRC) Space group number',
	'name': 'mrc_ispg',
	'vartype': 'int'
}, {
	'desc_long': 'Number of chars used for storing symmetry operators',
	'desc_short': '(MRC) Symmetry operator size',
	'property': 'bytes',
	'defaultunits': 'B',
	'name': 'mrc_nsymbt',
	'vartype': 'int'
}, {
	'desc_long': 'Machine stamp in CCP4 convention: big endian=0x11110000 little endian=0x44440000',
	'desc_short': '(MRC) Machine stamp',
	'name': 'mrc_machinestamp',
	'vartype': 'int'
}, {
	'desc_short': '(MRC) RMS deviation from mean density',
	'name': 'mrc_rms',
	'vartype': 'float'
}, {
	'desc_short': '(MRC) Number of labels',
	'name': 'mrc_nlabels',
	'vartype': 'int'
}, {
	'desc_short': '(MRC) Labels',
	'name': 'mrc_label',
	'vartype': 'string',
	'iter': True
}, {
	'desc_long': 'Image number, index from 1 to n',
	'desc_short': '(MRC) Image number',
	'name': 'imagic_imgnum',
	'vartype': 'int'
}, {
	'desc_long': 'Total number of images - 1',
	'desc_short': '(MRC) Image count',
	'name': 'imagic_count',
	'vartype': 'int'
}, {
	'desc_short': '(IMAGIC) Error code',
	'name': 'imagic_error',
	'vartype': 'int'
}, {
	'desc_long': 'Number of header records per image (Always 1)',
	'desc_short': '(IMAGIC) Header records per image',
	'name': 'imagic_headrec',
	'vartype': 'int'
}, {
	'desc_short': '(IMAGIC) Image creation (day)',
	'name': 'imagic_mday', 
	'vartype': 'int'
}, {
	'desc_short': '(IMAGIC) Image creation (month)',
	'name': 'imagic_month',
	'vartype': 'int'
}, {
	'desc_short': '(IMAGIC) Image creation (year)',
	'name': 'imagic_year', 
	'vartype': 'int'
}, {
	'desc_short': '(IMAGIC) Image creation (hour)',
	'name': 'imagic_hour', 
	'vartype': 'int'
}, {
	'desc_short': '(IMAGIC) Image creation (minute)',
	'name': 'imagic_minute',
	'vartype': 'int'
}, {
	'desc_short': '(IMAGIC) Image creation (second)',
	'name': 'imagic_sec',
	'vartype': 'int'
}, {
	'desc_short': '(IMAGIC) Image size in reals',
	'name': 'imagic_reals',
	'vartype': 'int'
}, {
	'desc_short': '(IMAGIC) Image size in pixels',
	'name': 'imagic_pixels',
	'vartype': 'int'
}, {
	'desc_long': 'IMAGIC file types: PACK, INTG, REAL, COMP, RECO',
	'desc_short': '(IMAGIC) Image type',
	'name': 'imagic_type',
	'vartype': 'string'
}, {
	'desc_long': 'Top left X coordinate in image before windowing',
	'desc_short': '(IMAGIC, old) Top left X coordinate',
	'name': 'imagic_ixold',
	'vartype': 'int'
}, {
	'desc_long': 'Top left Y coordinate in image before windowing',
	'desc_short': '(IMAGIC, old) Top left Y coordinate',
	'name': 'imagic_iyold',
	'vartype': 'int'
}, {
	'desc_short': '(IMAGIC, old) Average density',
	'name': 'imagic_oldav',
	'vartype': 'float'
}, {
	'desc_short': '(IMAGIC) Image ID',
	'name': 'imagic_label', 
	'vartype': 'string'
}, {
	'desc_long': 'Number of slices in volume; 1 for a 2D image',
	'desc_short': '(SPIDER) Slices in volume',
	'name': 'spider_nslice',
	'vartype': 'int'
}, {
	'desc_short': '(SPIDER) File type',
	'name': 'spider_type', 
	'vartype': 'int'
}, {
	'desc_short': '(SPIDER) Total number of records in file',
	'name': 'spider_irec',
	'vartype': 'float'
}, {
	'desc_long': 'This flag is 1 if tilt angles have been computed',
	'desc_short': '(SPIDER) Tilt angles computed flag',
	'name': 'spider_angvalid',
	'vartype': 'int'
}, {
	'desc_short': '(SPIDER) Tilt angle (Phi)',
	'name': 'spider_phi', 
	'vartype': 'float'
}, {
	'desc_short': '(SPIDER) Tilt angle (Theta)',
	'name': 'spider_theta', 
	'vartype': 'float'
}, {
	'desc_short': '(SPIDER) Tilt angle (Gamma)',
	'name': 'spider_gamma', 
	'vartype': 'float'
}, {
	'desc_short': '(SPIDER) Records in header',
	'name': 'spider_headrec',
	'vartype': 'int'
}, {
	'desc_short': '(SPIDER) Header length',
	'property': 'bytes',
	'defaultunits': 'B',
	'name': 'spider_headlen',
	'vartype': 'int'
}, {
	'desc_short': '(SPIDER) Record length',
	'property': 'bytes',
	'defaultunits': 'B',
	'name': 'spider_reclen',
	'vartype': 'int'
}, {
	'desc_short': '(SPIDER) Translation (X)',
	'name': 'spider_dx', 
	'vartype': 'float'
}, {
	'desc_short': '(SPIDER) Translation (Y)',
	'name': 'spider_dy', 
	'vartype': 'float'
}, {
	'desc_short': '(SPIDER) Translation (Z)',
	'name': 'spider_dz', 
	'vartype': 'float'
}, {
	'desc_long': 'This flag is 0 for simple 2D or 3D (non-stack) files. for stacked image, istack=2 in overall header, istack =-1 in following individual images.',
	'desc_short': '(SPIDER) Stack flag',
	'name': 'spider_istack',
	'vartype': 'int'
}, {
	'desc_long': 'Maxim is only used in the overall header for a stacked image file. It is the number of the highest image currently used in the stack. The number is updated, if necessary, when an image is added or deleted from the stack.',
	'desc_short': '(SPIDER) Last image in stack',
	'name': 'spider_maxim',
	'vartype': 'int'
}, {
	'desc_long': 'Imgnum is only used in a stacked image header. It is the number of the current image or zero if the image is unused.',
	'desc_short': '(SPIDER) Current image in stack',
	'name': 'spider_imgnum',
	'vartype': 'int'
}, {
	'desc_long': 'Flag that additional angles are present in header. 1 = one additional rotation is present, 2 = additional rotation that preceeds the rotation that was stored in words 15..20.',
	'desc_short': '(SPIDER) Additional angles flag',
	'name': 'spider_k_angle',
	'vartype': 'int'
}, {
	'desc_short': '(SPIDER) Phi 1',
	'name': 'spider_phi1', 
	'vartype': 'float'
}, {
	'desc_short': '(SPIDER) Theta 1',
	'name': 'spider_theta1', 
	'vartype': 'float'
}, {
	'desc_short': '(SPIDER) Psi 1',
	'name': 'spider_psi1', 
	'vartype': 'float'
}, {
	'desc_short': '(SPIDER) Phi 2',
	'name': 'spider_phi2', 
	'vartype': 'float'
}, {
	'desc_short': '(SPIDER) Theta 2',
	'name': 'spider_theta2', 
	'vartype': 'float'
}, {
	'desc_short': '(SPIDER) Psi 2',
	'name': 'spider_psi2', 
	'vartype': 'float'
}, {
	'desc_short': '(SPIDER) Created (date)',
	'name': 'spider_date', 
	'vartype': 'string'
}, {
	'desc_short': '(SPIDER) Create (time)',
	'name': 'spider_time', 
	'vartype': 'string'
}, {
	'desc_short': '(SPIDER) Title',
	'name': 'spider_title', 
	'vartype': 'string'
}, {
	'desc_short': '(SPIDER) Scale factor',
	'name': 'spider_scale', 
	'vartype': 'float'
}, {
	'desc_short': '(TIFF) Bits per pixel sample',
	'name': 'tiff_bitspersample',
	'vartype': 'int'
}, {
	'desc_short': '(TIFF) Resolution (X)',
	'name': 'tiff_resolution_x',
	'vartype': 'float'
}, {
	'desc_short': '(TIFF) Resolution (Y)',
	'name': 'tiff_resolution_y',
	'vartype': 'float'
}, {
	'desc_short': '(DM3) Acquisition (date)',
	'name': 'dm3_acq_date',
	'vartype': 'string'
}, {
	'desc_short': '(DM3) Acquisition (time)',
	'name': 'dm3_acq_time',
	'vartype': 'string'
}, {
	'desc_short': '(DM3) Actual magnification',
	'name': 'dm3_actual_mag',
	'vartype': 'float'
}, {
	'desc_short': '(DM3) Anti-blooming',
	'name': 'dm3_antiblooming',
	'vartype': 'int'
}, {
	'desc_short': '(DM3) Binning (X)',
	'name': 'dm3_binning_x',
	'vartype': 'int'
}, {
	'desc_short': '(DM3) Binning (Y)',
	'name': 'dm3_binning_y',
	'vartype': 'int'
}, {
	'desc_short': '(DM3) Camera size (X)',
	'name': 'dm3_camera_x',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_short': '(DM3) Camera size (Y)',
	'name': 'dm3_camera_y',
	'vartype': 'int',
	'property': 'count',
	'defaultunits': 'pixel'
}, {
	'desc_short': '(DM3) Microscope Cs',
	'name': 'dm3_cs',
	'vartype': 'float'
}, {
	'desc_short': '(DM3) Exposure number',
	'name': 'dm3_exposure_number',
	'vartype': 'int'
}, {
	'desc_short': '(DM3) Exposure time',
	'name': 'dm3_exposure_time',
	'vartype': 'float'
}, {
	'desc_short': '(DM3) Frame type',
	'name': 'dm3_frame_type',
	'vartype': 'string'
}, {
	'desc_short': '(DM3) Indicated magnification',
	'name': 'dm3_indicated_mag',
	'vartype': 'float'
}, {
	'desc_short': '(DM3) Filename',
	'name': 'dm3_name',
	'vartype': 'string'
}, {
	'desc_short': '(DM3) Pixel size',
	'name': 'dm3_pixel_size',
	'vartype': 'float',
	'property': 'length',
	'defaultunits': 'um'
}, {
	'desc_short': '(DM3) Camera name',
	'name': 'dm3_source',
	'vartype': 'string'
}, {
	'desc_short': '(DM3) Microscope voltage',
	'name': 'dm3_voltage',
	'vartype': 'float',
	'property': 'voltage',
	'defaultunits': 'V'
}, {
	'desc_short': '(DM3) Zoom',
	'name': 'dm3_zoom',
	'vartype': 'float'
}, {
	'desc_short': '(SerialEM) Tilt Angles',
	'name': 'serialem_tilts_angle',
	'vartype': 'float',
	'iter': True
}, {
	'desc_short': '(SerialEM) Tilt Doses',
	'name': 'serialem_tilts_dose',
	'vartype': 'float',
	'iter': True
}, {
	'desc_short': '(SerialEM) Tilt Magnifications',
	'name': 'serialem_tilts_magnification',
	'vartype': 'float',
	'iter': True
}, {
	'desc_short': '(SerialEM) Tilt Dose',
	'name': 'serialem_tilt_dose',
	'vartype': 'float'
}, {
	'desc_short': '(SerialEM) Tilt Intensity',
	'name': 'serialem_tilt_intensity',
	'vartype': 'float'
}, {
	'desc_short': '(SerialEM) Tilt Magnification',
	'name': 'serialem_tilt_magnification',
	'vartype': 'float'
}, {
	'desc_short': '(SerialEM) Tilt Montage',
	'name': 'serialem_tilt_montage',
	'vartype': 'float',
	'iter': True,
}, {
	# got to here
	'desc_short': '(SerialEM) Tilt Stage (X)',
	'name': 'serialem_tilt_angle',
	'vartype': 'float'
}, {
	'desc_short': '(SerialEM) Tilt Angle',
	'name': 'serialem_tilt_angle',
	'vartype': 'float'
}, {
	'desc_short': '(SerialEM) Tilt Angle',
	'name': 'serialem_tilt_angle',
	'vartype': 'float'
}]


recorddefs = []


if __name__ == "__main__":
	if os.path.exists(sys.argv[1]):
		print "Warning: File %s exists"%sys.argv[1]
	print "Saving output to %s"%sys.argv[1]
	print "ParamDefs:"
	print set([i.get('name') for i in paramdefs])
	print "RecordDefs:"
	print set([i.get('name') for i in recorddefs])

	with open(sys.argv[1],'w') as f:
		for pd in paramdefs:
			pd['keytype'] = 'paramdef'
			pd['uri'] = 'http://ncmidb.bcm.edu/paramdef/%s'%pd['name']
			f.write(json.dumps(pd)+"\n")
		for rd in recorddefs:
			rd['keytype'] = 'recorddef'
			rd['uri'] = 'http://ncmidb.bcm.edu/recorddef/%s'%rd['name']
			f.write(json.dumps(rd)+"\n")



