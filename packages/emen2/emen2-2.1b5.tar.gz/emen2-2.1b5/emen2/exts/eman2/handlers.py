# $Id: handlers.py,v 1.21 2012/03/08 11:29:26 irees Exp $
'''File handlers
'''
import time
import math
import os
import signal
import struct
import json
import cPickle as pickle

# For file writing
import tempfile

# EMEN2 imports
import emen2.db.handlers
BinaryHandler = emen2.db.handlers.BinaryHandler

try:
	import EMAN2
	# We need to steal these handlers back from EMAN2...
	signal.signal(2, signal.SIG_DFL)
	signal.signal(15, signal.SIG_DFL)
except ImportError:
	EMAN2 = None


# Known EMData Header Parameters
emdata_params = set([
	'dm3_acq_date',
	'dm3_acq_time',
	'dm3_actual_mag',
	'dm3_antiblooming',
	'dm3_binning_x',
	'dm3_binning_y',
	'dm3_camera_x',
	'dm3_camera_y',
	'dm3_cs',
	'dm3_exposure_number',
	'dm3_exposure_time',
	'dm3_frame_type',
	'dm3_indicated_mag',
	'dm3_name',
	'dm3_pixel_size',
	'dm3_source',
	'dm3_voltage',
	'dm3_zoom',
	'emdata_apix_x',
	'emdata_apix_y',
	'emdata_apix_z',
	'emdata_changecount',
	'emdata_class_id',
	'emdata_class_ptcl_idxs',
	'emdata_class_ptcl_src',
	'emdata_ctf_phase_flipped',
	'emdata_ctf_snr_total',
	'emdata_ctf_wiener_filtered',
	'emdata_data_n',
	'emdata_data_path',
	'emdata_data_source',
	'emdata_datatype',
	'emdata_eigval',
	'emdata_exc_class_ptcl_idxs',
	'emdata_hostendian',
	'emdata_is_complex',
	'emdata_is_complex_ri',
	'emdata_kurtosis',
	'emdata_match_n',
	'emdata_match_qual',
	'emdata_maximum',
	'emdata_mean',
	'emdata_mean_nonzero',
	'emdata_median',
	'emdata_microscope_cs',
	'emdata_microscope_voltage',
	'emdata_minimum',
	'emdata_model_id',
	'emdata_nonzero_median',
	'emdata_nx',
	'emdata_ny',
	'emdata_nz',
	'emdata_origin_x',
	'emdata_origin_y',
	'emdata_origin_z',
	'emdata_projection_image',
	'emdata_projection_image_idx',
	'emdata_ptcl_helix_coords',
	'emdata_ptcl_repr',
	'emdata_ptcl_source_coord',
	'emdata_ptcl_source_image',
	'emdata_reconstruct_norm',
	'emdata_reconstruct_preproc',
	'emdata_reconstruct_qual',
	'emdata_render_max',
	'emdata_render_min',
	'emdata_segment_centers',
	'emdata_sigma',
	'emdata_sigma_nonzero',
	'emdata_skewness',
	'emdata_source_n',
	'emdata_source_path',
	'emdata_square_sum',
	'emdata_subvolume_full_nx',
	'emdata_subvolume_full_ny',
	'emdata_subvolume_full_nz',
	'emdata_subvolume_x0',
	'emdata_subvolume_y0',
	'emdata_subvolume_z0',
	'emdata_threed_excl_ptcl_idxs',
	'emdata_threed_ptcl_idxs',
	'emdata_threed_ptcl_src',
	'imagic_count',
	'imagic_error',
	'imagic_headrec',
	'imagic_hour',
	'imagic_imgnum',
	'imagic_ixold',
	'imagic_iyold',
	'imagic_label',
	'imagic_mday',
	'imagic_minute',
	'imagic_month',
	'imagic_oldav',
	'imagic_pixels',
	'imagic_reals',
	'imagic_sec',
	'imagic_type',
	'imagic_year',
	'mrc_alpha',
	'mrc_beta',
	'mrc_gamma',
	'mrc_ispg',
	'mrc_machinestamp',
	'mrc_mapc',
	'mrc_mapr',
	'mrc_maps',
	'mrc_maximum',
	'mrc_mean',
	'mrc_minimum',
	'mrc_mx',
	'mrc_my',
	'mrc_mz',
	'mrc_nlabels',
	'mrc_nsymbt',
	'mrc_nx',
	'mrc_nxstart',
	'mrc_ny',
	'mrc_nystart',
	'mrc_nz',
	'mrc_nzstart',
	'mrc_rms',
	'mrc_xlen',
	'mrc_ylen',
	'mrc_zlen',
	'serialem_tilt_angle',
	'serialem_tilt_dose',
	'serialem_tilt_intensity',
	'serialem_tilt_magnification',
	'serialem_tilt_montage',
	'serialem_tilts_angle',
	'serialem_tilts_dose',
	'serialem_tilts_magnification',
	'spider_angvalid',
	'spider_date',
	'spider_dx',
	'spider_dy',
	'spider_dz',
	'spider_gamma',
	'spider_headlen',
	'spider_headrec',
	'spider_imgnum',
	'spider_irec',
	'spider_istack',
	'spider_k_angle',
	'spider_maxim',
	'spider_nslice',
	'spider_phi',
	'spider_phi1',
	'spider_phi2',
	'spider_psi1',
	'spider_psi2',
	'spider_reclen',
	'spider_scale',
	'spider_theta',
	'spider_theta1',
	'spider_theta2',
	'spider_time',
	'spider_title',
	'spider_type',
	'tiff_bitspersample',
	'tiff_resolution_x',
	'tiff_resolution_y'
])


def emdata_rename(header):
	'''Convert EMData attributes to EMEN2 parameter names.'''
	ret = {}
	prefixes = ['mrc', 'dm3', 'tiff', 'imagic', 'spider']
	mrclabels = []
	
	for k,v in header.items():
		if k.startswith('MRC.label'):
			mrclabels.append(v)
			continue
		
		# Rename the key
		pre, _, post = k.rpartition(".")
		pre = pre or "emdata"
		k = '%s_%s'%(pre.lower(), post)
		if k in emdata_params:
			ret[k] = v
		# else:
		#	print "Skipping unknown EMData key:", k

	if mrclabels:
		ret['mrc_label'] = mrclabels

	# Remove the source path; it will just point to a tmp file.
	ret.pop('emdata_source_path', None)
	return ret


def sign(a):
	if a>0: return 1
	return -1



class EMDataBuilder(object):
	def build_tiles(self, img, outfile, tilesize=256):
		# Make a temporary directory
		tmpdir = tempfile.mkdtemp(prefix='emen2thumbs')

		# Work with a copy of the EMData
		img2 = img.copy()
		
		# Calculate the number of zoom levels based on the tile size
		levels = math.ceil( math.log( max(img.get_xsize(), img.get_ysize()) / tilesize) / math.log(2.0) )

		# Tile header
		header = img.get_attr_dict()
		tile_dict = {}
		# tile_dict['emdata'] = header
		# tile_dict['nx'] = header.get('nx')
		# tile_dict['ny'] = header.get('ny')
		# tile_dict['nz'] = header.get('nz')
		# tile_dict['tilesize'] = tilesize
		# tile keys...
		# (z, x, y, level)
		# ...for: 
		# 	pos, offset
		# 	width, height
		
		# Step through nz...

		# Step through shrink range creating tiles
		pos = 0
		xs, ys = img2.get_xsize(), img2.get_ysize()
		for l in range(int(levels)):
			rmin = img2.get_attr("mean") - img2.get_attr("sigma") * 3.0
			rmax = img2.get_attr("mean") + img2.get_attr("sigma") * 3.0
			for x in range(0, img2.get_xsize(), tilesize):
				for y in range(0, img2.get_ysize(), tilesize):
					i = img2.get_clip(EMAN2.Region(x, y, tilesize, tilesize), fill=rmax)
					i.set_attr("render_min", rmin)
					i.set_attr("render_max", rmax)
					i.set_attr("jpeg_quality", 80)
					fsp = "%s/%d.%03d.%03d.jpg"%(tmpdir, l, x/tilesize, y/tilesize)
					i.write_image(fsp)
					sz = os.stat(fsp).st_size
					tile_dict[(l, x/tilesize, y/tilesize)] = (pos,sz)
					pos += sz

			img2.process_inplace("math.meanshrink",{"n":2})

		# Copy all the tiles into the .tile pickle file
		tf = file(outfile, "w")
		pickle.dump(tile_dict, tf)
		for l in range(int(levels)):
			for x in range(0, xs, tilesize):
				for y in range(0, ys, tilesize):
					fsp = "%s/%d.%03d.%03d.jpg"%(tmpdir, l, x/tilesize, y/tilesize)
					a = file(fsp,"r")
					b = a.read()
					a.close()
					tf.write(b)
					os.remove(fsp)
			xs /= 2
			ys /= 2
		tf.close()
			
		# Cleanup	
		os.rmdir(tmpdir)	


	def _build_pspec(self, img, outfile, outfile1d=None):
		# This will produce 2 power spectrum images in the tile file
		nx, ny = img.get_xsize() / 512, img.get_ysize() / 512

		a = EMAN2.EMData()
		a.set_size(512,512)

		if (ny>2 and nx>2):
			for y in range(1,ny-1):
				for x in range(1,nx-1):
					c = img.get_clip(EMAN2.Region(x*512,y*512,512,512))
					try:
						c.process_inplace("normalize")
					except:
						c.process_inplace("eman1.normalize")
					c.process_inplace("math.realtofft")
					c.process_inplace("math.squared")
					a += c

			# Reset the center value
			a.set_value_at(256, 256, 0, .01)

			# Adjust brightness
			a -= a.get_attr("minimum") - a.get_attr("sigma") * .01
			a.process_inplace("math.log")
			a.set_attr("render_min", a.get_attr("minimum") - a.get_attr("sigma") * .1)
			a.set_attr("render_max", a.get_attr("mean") + a.get_attr("sigma") * 4.0)

			# Write out the PSpec png
			a.write_image(outfile)

		if outfile1d:
			# Write out the 1D averaged power spectrum
			x = range(0,255) # numpy.arange(0,255,1.0)
			y = a.calc_radial_dist(255,1,1,0) # radial power spectrum (log)
			f = open(outfile1d, "w")
			json.dump(y,f)
			f.close()
	
	
	def build_scale(self, img, outfile, tilesize=256):
		# print "Building scaled image: %s %s"%(tilesize, outfile)
		# Get the scale factor
		thumb_scale = img.get_xsize()/float(tilesize), img.get_ysize()/float(tilesize)
		sc = math.ceil(max(thumb_scale))
		
		# Shrink the image
		img2 = img.process("math.meanshrink", {"n":sc})

		# Adjust the brightness for rendering
		rmin = img2.get_attr("mean") - img2.get_attr("sigma") * 3.0
		rmax = img2.get_attr("mean") + img2.get_attr("sigma") * 3.0
		img2.set_attr("render_min", rmin)
		img2.set_attr("render_max", rmax)
		img2.set_attr("jpeg_quality", 80)		
		img2.write_image(outfile)
	

	def tile_info(self, tilefile):
		"""Extract dictionary of tiles from a tilefile"""
		tf = file(tilefile,"r")
		td = pickle.load(tf)
		tf.close()
		return td


	def tile_read(self, tilefile, level, x, y):
		"""Retrieve a tile from the file"""
		tf = file(tilefile,"r")
		td = pickle.load(tf)
		a = td[(level,x,y)]
		tf.seek(a[0],1)
		ret = tf.read(a[1])
		tf.close()
		return ret




##### Cryo-EM file format handlers #####

class EMDataHandler(BinaryHandler):
	_allow_gzip = True
	def _thumbnail_build(self, workfile, **kwargs):
		pass
			
			
			

@BinaryHandler.register(['dm3', 'mrc', 'tif', 'tiff'])
class MicrographHandler(EMDataHandler):
	_allow_gzip = True
	
	def extract(self, **kwargs):
		# Get the basic header from EMAN2
		workfile = str(self._getfilepath())

		img = EMAN2.EMData()
		img.read_image(workfile, 0, True)
		header = img.get_attr_dict()
		header = emdata_rename(header)
		c = {
			'dm3_source':'ccd_id',
			'dm3_frame_type':'type_frame',
			'dm3_exposure_number':'id_ccd_frame',
			'dm3_binning_x':'binning',
			'emdata_nx':'size_image_ccd_x',
			'emdata_ny':'size_image_ccd_y',
			'emdata_apix_x':'angstroms_per_pixel',
		}
		for v,k in c.items():
			if header.get(k) is None:
				header[k] = header.get(v)

		# Convert
		return header

	def _thumbnail_build(self, workfile):
		# print "Building using..:", workfile
		img = EMAN2.EMData()
		# EMAN2 does not like unicode filenames
		img.read_image(str(workfile))
		img.process_inplace("normalize")
		builder = EMDataBuilder()
		builder.build_tiles(img, self._outfile('tile'))
		# builder.build_pspec(img, self.outfile('pspec.png'), outfile1d=self.outfile('radial.txt'))
		builder.build_scale(img, self._outfile('thumb.jpg'), tilesize=128)
		builder.build_scale(img, self._outfile('small.jpg'), tilesize=512)
		builder.build_scale(img, self._outfile('medium.jpg'), tilesize=1024)

		

		





@BinaryHandler.register(['st'])
class SerialEMHandler(EMDataHandler):
	_allow_gzip = False
	
	# IMOD SerialEM format
	# http://bio3d.colorado.edu/imod/doc/guide.html	

	# Start at a 92 byte offset (standard MRC header attributes)
	# Then read in the following SerialEM Headers.
	# [target parameter, C struct type, default value]
	header_labels = [
		# Number of bytes in extended header
		['serialem_extheadersize', 'i', 0],
		# Creator ID, creatid
		['serialem_creatid', 'h', 0],
		# 30 bytes of unused data
		[None, '30s', ''],
		## Number of bytes per section (SerialEM format) of extended header
		['serialem_bytespersection', 'h', 0],
		# Flags for which types of short data (SerialEM format), nreal. (See extheader_flags)
		['serialem_extheaderflags', 'h', 0],
		# 28 bytes of unused data
		[None, '28s', ''],
		# Additional SerialEM attributes
		['serialem_idtype', 'h', 0],
		['serialem_lens', 'h', 0],
		['serialem_nd1', 'h', 0],
		['serialem_nd2', 'h', 0],
		['serialem_vd1', 'h', 0],
		['serialem_vd2', 'h', 0],
		['serialem_tiltangles_orig', 'fff', [0.0, 0.0, 0.0]],
		['serialem_tiltangles_current', 'fff', [0.0, 0.0, 0.0]],
		['serialem_xorg', 'f', 0.0],
		['serialem_yorg', 'f', 0.0],
		['serialem_zorg', 'f', 0.0],
		['serialem_cmap', '4s', '']
	]

	# The SerialEM extended header is a mask
	# Compare with the following keys to find the attributes
	extheader_flags = {
		1: {'pack': 'h',
			'load': lambda x:[x[0] / 100.0],
			'dump': lambda x:[x[0] * 100],
			'dest':  ['serialem_tilt'],
			'also': ['specimen_tilt']},

		2: {'pack': 'hhh',
			'load': lambda x:[x],
			'dump': lambda x:[x],
			'dest': ['serialem_montage']},

		4: {'pack': 'hh',
			'load': lambda x:[x[0] / 25.0 , x[1] / 25.0],
			'dump': lambda x:[x[0] * 25   , x[1] * 25],
			'dest': ['serialem_stage_x', 'serialem_stage_y'],
			'also': ['position_stage_x', 'position_stage_y']},

		8: {'pack': 'h',
			'load': lambda x:[x[0] / 10.0],
			'dump': lambda x:[x[0] * 10],
			'dest': ['serialem_magnification'],
			'also': ['tem_magnification_set']},

		16: {'pack': 'h',
			'load': lambda x:[x[0] / 25000.0],
			'dump': lambda x:[x[0] * 25000],
			'dest': ['serialem_intensity']},

		32: {'pack': 'hh',
			'load': lambda x:[sign(x[0])*(math.fabs(x[0])*256+(math.fabs(x[1])%256))*2**(sign(x[1])*(int(math.fabs(x[1]))/256))],
			'dump': lambda x:[0,0],
			'dest': ['serialem_dose']}
	}


	def _thumbnail_build(self, workfile):
		# print "Building using..:", workfile
		workfile = str(workfile)
		img = EMAN2.EMData()
		img.read_image(workfile, 0, True)
		header = img.get_attr_dict()
	
		# Read the middle frame
		region = EMAN2.Region(0, 0, header['nz']/2, header['nx'], header['ny'], 1)
		img = EMAN2.EMData()
		img.read_image(workfile, 0, False, region)
		img.process_inplace("normalize")
		
		builder = EMDataBuilder()
		builder.build_tiles(img, self._outfile('tile'))
		# builder.build_pspec(img, self._outfile('pspec.png'), outfile1d=self._outfile('radial.txt'))
		builder.build_scale(img, self._outfile('thumb.jpg'), tilesize=128)
		builder.build_scale(img, self._outfile('small.jpg'), tilesize=512)
		builder.build_scale(img, self._outfile('medium.jpg'), tilesize=1024)

		
	def extract(self, **kwargs):
		workfile = str(self._getfilepath())
	
		# Get the basic header from EMAN2
		img = EMAN2.EMData()
		img.read_image(workfile, 0, True)
		header = img.get_attr_dict()

		# Read the SerialEM header and extended header
		# print "Reading extended stack header..."

		# ... get the extheader information
		header.update(self._get_serielem_header(workfile))

		# ... read
		extheader = self._get_serielem_extheader(workfile, header['serialem_extheadersize'], header['nz'], header['serialem_extheaderflags'])
		tilts = filter(lambda x:x!=None, [i.get('serialem_tilt') for i in extheader])
		if tilts:
			header["serialem_maxangle"] = max(tilts)
			header["serialem_minangle"] = min(tilts)
	
		h = emdata_rename(header)
		# print "Header:", h
	
		# Convert
		return {}


	##### Read SerialEM extended header #####
	
	def _get_serielem_header(self, workfile, offset=92):
		"""Extract data from header string (1024 bytes) and process"""
		f = open(workfile,"rb")
		hdata = f.read(1024)
		f.close()
		
		d={}
		for dest, format, default in self.header_labels:
			size = struct.calcsize(format)
			value = struct.unpack(format, hdata[offset:offset+size])
			if dest == None:
				pass
			elif len(value) == 1:
				d[dest] = value[0]
			else:
				d[dest] = value
			offset += size
		return d


	def _get_serielem_extheader(self, workfile, serialem_extheadersize, nz, flags):
		"""Process extended header"""

		f = open(workfile,"rb")
		hdata = f.read(1024)
		ehdata = f.read(serialem_extheadersize)
		f.close()

		ed = []
		offset = 0

		# Get the extended header attributes
		keys = self._extheader_getkeys(flags)

		# For each slice..
		for i in range(0, nz):
			sslice = {}

			# Process each extended header attribute
			for key in keys:
				# Get the flags and calculate the size
				parser = self.extheader_flags.get(key)
				size = struct.calcsize(parser['pack'])

				# Parse the section
				# print "Consuming %s bytes (%s:%s) for %s"%(size, i+offset, i+offset+size, parser['dest'])
				value = struct.unpack(parser['pack'], ehdata[offset: offset+size])

				# Process the packed value
				value = parser['load'](value)

				# Update the slice
				for dest,v in zip(parser.get('dest', []), value):
					sslice[dest] = v
				for dest,v in zip(parser.get('also', []), value):
					sslice[dest] = v

				# Read the next section
				offset += size

			ed.append(sslice)

		return ed

	def _extheader_getkeys(self, flags):
		keys = []
		for i in sorted(self.extheader_flags.keys()):
			if flags & i:
				keys.append(i)
		return keys



class DDDHandler(BinaryHandler):
	ddd_mapping = {
		'Binning X': 'binning_x',
		'Binning Y': 'binning_y',
		'Camera Position': 'camera_position',
		'Dark Correction': 'ddd_dark_correction',
		'Dark Frame Status': 'ddd_dark_frame_status',
		'Data Output Mode': 'ddd_data_output_mode',
		'Exposure Mode': 'ddd_exposure_mode',
		'FPGA Version': 'ddd_fpga_version',
		'Faraday Plate Peak Reading During Last Exposure': 'faraday_plate_peak',
		'Gain Correction': 'ddd_gain_correction',
		'Gain Frame Status': 'ddd_gain_frame_status',
		'Hardware Binning X': 'binning_hardware_x',
		'Hardware Binning Y': 'binning_hardware_y',
		'Last Dark Frame Dataset': 'ddd_last_dark_frame_dataset',
		'Last Gain Frame Dataset': 'ddd_last_gain_frame_dataset',
		'Preexposure Time in Seconds': 'time_preexposure',
		'ROI Offset H': 'roi_offset_h',
		'ROI Offset W': 'roi_offset_w',
		'ROI Offset X': 'roi_offset_x',
		'ROI Offset Y': 'roi_offset_y',
		'Raw Frames Filename Suffix': 'ddd_raw_frame_suffix',
		'Raw Frames Type': 'ddd_raw_frame_type',
		'Save Raw Frames': 'ddd_raw_frame_save',
		'Save Summed Image': 'ddd_raw_frame_save_summed',
		'Screen Position': 'screen_position',
		'Sensor Coarse Gain': 'ddd_sensor_coarse_gain',
		'Sensor Offset': 'ddd_sensor_offset',
		'Sensor Output Mode': 'ddd_sensor_output_mode',
		'Temperature Cold Finger (Celsius)': 'ddd_temperature_cold_finger',
		'Temperature Control': 'ddd_temperature_control',
		'Temperature Control Mode': 'ddd_temperature_control_mode',
		'Temperature Detector (Celsius)': 'ddd_temperature_detector',
		'Temperature TEC Current (Ampere)': 'ddd_temperature_tec_current',
		'Temperature Water Line (Celsius)': 'ddd_temperature_water_line',
		'Vacuum Level': 'vacuum_level'
	}

	# def load_ddd_metadata(self):
	# 	foundfiles = []
	# 	ret = {}
	# 	infoname = os.path.join(os.path.dirname(self.filename), 'info.txt')
	# 	print "Checking:", infoname
	# 	if os.path.exists(infoname):
	# 		f = open(infoname)
	# 		data = f.readlines()
	# 		f.close()
	# 		for line in data:
	# 			param, _, value = line.strip().partition("=")
	# 			mapparam = self.ddd_mapping.get(param)
	# 			if mapparam:
	# 				# print 'param %s -> %s: %s'%(param, mapparam, value)
	# 				ret[mapparam] = value
	# 
	# 		foundfiles.append(infoname)			
	# 	return ret, foundfiles	
	# 
	# def get_upload_items(self):
	# 	ddd_params, foundfiles = self.load_ddd_metadata()
	# 	newrecord = {}
	# 	newrecord["name"] = -100
	# 	newrecord["rectype"] = "ddd"
	# 	newrecord.update(self.applyparams)
	# 	newrecord.update(ddd_params)
	# 	newrecord["parents"] = [self.name]
	# 	dname = os.path.split(os.path.dirname(self.filename))[-1]
	# 	fname = os.path.basename(self.filename)
	# 	uploadname = '%s-%s'%(dname, fname)
	# 	newrecord['id_ccd_frame'] = uploadname
	# 
	# 	files = [emdash.transport.UploadTransport(name=-100, uploadname=uploadname, filename=self.filename, param='file_binary_image')]
	# 	files[0].newrecord = newrecord		
	# 
	# 	for i in foundfiles:
	# 		files.append(emdash.transport.UploadTransport(name=-100, filename=i, uploadname='%s-%s'%(dname, os.path.basename(i)), compress=False))
	# 
	# 	return files




class JADASHandler(BinaryHandler):
	pass
	# rectype = 'ccd_jadas'
	# 
	# def get_upload_items(self):
	# 	# This is run for a .tif file produced by JADAS. Find the associated .xml files, load them, map as many
	# 	# parameters as possible, and attach the raw xml file.
	# 	jadas_params, foundfiles = self.load_jadas_xml()
	# 	
	# 	newrecord = {}
	# 	newrecord["name"] = -100
	# 	newrecord["rectype"] = "ccd_jadas"
	# 	newrecord["id_micrograph"] = os.path.basename(self.filename)
	# 	newrecord.update(self.applyparams)
	# 	newrecord.update(jadas_params)
	# 	newrecord["parents"] = [self.name]
	# 	
	# 	files = [emdash.transport.UploadTransport(name=-100, filename=self.filename, param='file_binary_image')]
	# 	files[0].newrecord = newrecord
	# 	
	# 	for i in foundfiles:
	# 		files.append(emdash.transport.UploadTransport(name=-100, filename=i, compress=False))
	# 			
	# 	return files
	# 
	# 
	# def load_jadas_xml(self):
	# 	# find related XML files, according to JADAS naming conventions
	# 	# take off the .tif, because the xml could be either file.tif_metadata.xml or file_metadata.xml
	# 	if not ET:
	# 		raise ImportError, "The ElementTree package (xml.etree.ElementTree) is required"
	# 		
	# 	foundfiles = []
	# 	ret = {}		
	# 	for xmlfile in glob.glob('%s_*.xml'%self.filename) + glob.glob('%s_*.xml'%self.filename.replace('.tif','')):
	# 		print "Attempting to load ", xmlfile
	# 		try:
	# 			e = ET.parse(xmlfile)
	# 			root = e.getroot()
	# 			# There should be a loader for each root tag type, e.g. TemParameter -> map_jadas_TemParameter
	# 			loader = getattr(self, 'map_jadas_%s'%root.tag, None)
	# 			if loader:
	# 				ret.update(loader(root))
	# 				foundfiles.append(xmlfile)
	# 		except Exception, e:
	# 			print "Could not load %s: %s"%(xmlfile, e)
	# 
	# 	return ret, foundfiles
	# 
	# 
	# 
	# def map_jadas_TemParameter(self, root):
	# 	"""One of these long, ugly, metadata-mapping methods"""
	# 	ret = {}
	# 	# Defocus
	# 	ret['defocus_absdac'] = root.find('Defocus/defocus').get('absDac')
	# 	ret['defocus_realphysval'] = root.find('Defocus/defocus').get('relPhisVal')
	# 	ret['intendeddefocus_valinnm'] = root.find('Defocus/intendedDefocus').get('valInNm')
	# 	d = root.find('Defocus/intendedDefocus').get('valInNm')
	# 	if d != None:
	# 		d = float(d) / 1000.0
	# 		ret['ctf_defocus_set'] = d
	# 
	# 	# Eos
	# 	ret['eos_brightdarkmode'] = root.find('Eos/eos').get('brightDarkMode')
	# 	ret['eos_darklevel'] = root.find('Eos/eos').get('darkLevel')
	# 	ret['eos_stiglevel'] = root.find('Eos/eos').get('stigLevel')
	# 	ret['eos_temasidmode'] = root.find('Eos/eos').get('temAsidMode')
	# 	ret['eos_htlevel'] = root.find('Eos/eos').get('htLevel')
	# 	ret['eos_imagingmode'] = root.find('Eos/eos').get('imagingMode')
	# 	ret['eos_magcamindex'] = root.find('Eos/eos').get('magCamIndex')
	# 	ret['eos_spectrummode'] = root.find('Eos/eos').get('spectrumMode')
	# 	ret['eos_illuminationmode'] = root.find('Eos/eos').get('illuminationMode')
	# 	ret['eos_spot'] = root.find('Eos/eos').get('spot')
	# 	ret['eos_alpha'] = root.find('Eos/eos').get('alpha')
	# 
	# 	# Lens
	# 	ret['lens_cl1dac'] = root.find('Lens/lens').get('cl1Dac')
	# 	ret['lens_cl2dac'] = root.find('Lens/lens').get('cl2Dac')
	# 	ret['lens_cl3dac'] = root.find('Lens/lens').get('cl3Dac')
	# 	ret['lens_cmdac'] = root.find('Lens/lens').get('cmDac')
	# 	ret['lens_il1dac'] = root.find('Lens/lens').get('il1Dac')
	# 	ret['lens_il2dac'] = root.find('Lens/lens').get('il2Dac')
	# 	ret['lens_il3dac'] = root.find('Lens/lens').get('il3Dac')
	# 	ret['lens_il4dac'] = root.find('Lens/lens').get('il4Dac')
	# 	ret['lens_pl1dac'] = root.find('Lens/lens').get('pl1Dac')
	# 	ret['lens_pl2dac'] = root.find('Lens/lens').get('pl2Dac')
	# 	ret['lens_pl3dac'] = root.find('Lens/lens').get('pl3Dac')
	# 	
	# 	# Def
	# 	ret['def_gunshiftx'] = root.find('Def/def').get('gunShiftX')
	# 	ret['def_gunshifty'] = root.find('Def/def').get('gunShiftY')
	# 	ret['def_guntiltx'] = root.find('Def/def').get('gunTiltX')
	# 	ret['def_guntilty'] = root.find('Def/def').get('gunTiltY')
	# 	ret['def_beamshiftx'] = root.find('Def/def').get('beamShiftX')
	# 	ret['def_beamshifty'] = root.find('Def/def').get('beamShiftY')
	# 	ret['def_beamtiltx'] = root.find('Def/def').get('beamTiltX')
	# 	ret['def_beamtilty'] = root.find('Def/def').get('beamTiltY')			
	# 	ret['def_clstigx'] = root.find('Def/def').get('clStigX')
	# 	ret['def_clstigy'] = root.find('Def/def').get('clStigY')
	# 	ret['def_olstigx'] = root.find('Def/def').get('olStigX')
	# 	ret['def_olstigy'] = root.find('Def/def').get('olStigY')
	# 	ret['def_ilstigx'] = root.find('Def/def').get('ilStigX')
	# 	ret['def_ilstigy'] = root.find('Def/def').get('ilStigY')
	# 	ret['def_imageshiftx'] = root.find('Def/def').get('imageShiftX')
	# 	ret['def_imageshifty'] = root.find('Def/def').get('imageShiftY')
	# 	ret['def_plax'] = root.find('Def/def').get('plaX')
	# 	ret['def_play'] = root.find('Def/def').get('plaY')
	# 	
	# 	# HT
	# 	ret['ht_ht'] = root.find('HT/ht').get('ht')
	# 	ret['ht_energyshift'] = root.find('HT/ht').get('energyShift')
	# 	
	# 	# MDS
	# 	ret['mds_mdsmode'] = root.find('MDS/mds').get('mdsMode')
	# 	ret['mds_blankingdef'] = root.find('MDS/mds').get('blankingDef')
	# 	ret['mds_defx'] = root.find('MDS/mds').get('defX')
	# 	ret['mds_defy'] = root.find('MDS/mds').get('defY')
	# 	ret['mds_blankingtype'] = root.find('MDS/mds').get('blankingType')
	# 	ret['mds_blankingtime'] = root.find('MDS/mds').get('blankingTime')
	# 	ret['mds_shutterdelay'] = root.find('MDS/mds').get('shutterDelay')
	# 	
	# 	# Photo
	# 	ret['photo_exposuremode'] = root.find('PHOTO/photo').get('exposureMode')
	# 	ret['photo_manualexptime'] = root.find('PHOTO/photo').get('manualExpTime')
	# 	ret['photo_filmtext'] = root.find('PHOTO/photo').get('filmText')
	# 	ret['photo_filmnumber'] = root.find('PHOTO/photo').get('filmNumber')
	# 	
	# 	# GonioPos
	# 	ret['goniopos_x'] = root.find('GonioPos/gonioPos').get('x')
	# 	ret['goniopos_y'] = root.find('GonioPos/gonioPos').get('y')
	# 	ret['goniopos_z'] = root.find('GonioPos/gonioPos').get('z')
	# 	ret['goniopos_tiltx'] = root.find('GonioPos/gonioPos').get('tiltX')
	# 	ret['goniopos_rotortilty'] = root.find('GonioPos/gonioPos').get('rotOrTiltY')
	# 
	# 	return ret
	# 	
	# 	
	# 	
	# def map_jadas_DigitalCameraParameter(self, root):
	# 	attrmap = {
	# 		'CameraName': 'ccd_id',
	# 		'AreaTop': 'digicamprm_areatop',
	# 		'AreaBottom': 'digicamprm_areabottom',
	# 		'AreaLeft': 'digicamprm_arealeft',
	# 		'AreaRight': 'digicamprm_arearight',
	# 		'Exposure': 'time_exposure_tem',
	# 		'Binning': 'binning',
	# 		'PreIrradiation': 'digicamcond_preirradiation',
	# 		'BlankingTime': 'digicamcond_blankingtime',
	# 		'BlankBeam': 'digicamcond_blankbeam',
	# 		'CloseScreen': 'digicamcond_closescreen',
	# 		'DataFormat': 'digicamcond_dataformat'		
	# 	}
	# 
	# 	ret = {}
	# 	for i in root.findall('*/tagCamPrm'):
	# 		param = attrmap.get(i.get('tagAttrName'))
	# 		value = i.get('tagAttrVal')
	# 		if param != None and value != None:
	# 			ret[param] = value		
	# 
	# 	return ret
	# 	
	# 	
	# 	
	# def map_jadas_IntensityBasedHoleSelection(self, root):
	# 	ret = {}
	# 	return ret
	# 	




class ScanHandler(BinaryHandler):
	pass
	# rectype = 'scan'
	# 
	# request_params = [
	# 	'scanner_film',
	# 	'scanner_cartridge',
	# 	'scan_average',
	# 	'nikon_gain',
	# 	'scan_step',
	# 	'angstroms_per_pixel'
	# 	]
	# 
	# 
	# def get_upload_items(self):
	# 	print "Checking for existing micrograph..."
	# 	idmap = collections.defaultdict(set)
	# 	mc = self.db.getchildren(self.name, 1, "micrograph")
	# 	mc = self.db.getrecord(mc)
	# 	for rec in mc:
	# 		i = rec.get('id_micrograph', '').strip().lower()
	# 		idmap[i].add(rec.get('name'))
	# 
	# 	outfile = self.filename
	# 
	# 	# This is an ugly hack until I think of a better way
	# 	opts = {}
	# 	try:
	# 		# tif2mrc, bin, invert, odconversion
	# 		for i in ['tif2mrc', 'bin', 'invert', 'odconversion']:
	# 			opts[i] = emdash.config.get(i)
	# 			# getattr(emdash.config, i, None)
	# 		print "Using options for ScanHandler:", opts
	# 	except:
	# 		pass
	# 
	# 	if opts.get('tif2mrc'):
	# 		outfile = outfile.replace('.tif', '.mrc')
	# 		args = []
	# 		# if python:
	# 		# 	args.append(python)
	# 		args.append('nikontiff2mrc.py')
	# 		if opts.get('bin') != None:
	# 			args.append('--bin=%s'%opts.get('bin'))
	# 		if opts.get('invert') != None:
	# 			args.append('--invert=%s'%opts.get('invert'))
	# 		if opts.get('odconversion') != None:
	# 			args.append('--ODconversion=%s'%opts.get('odconversion'))
	# 
	# 		args.append(self.filename)
	# 		args.append(outfile)
	# 		
	# 		print "running: %s"%args
	# 		a = subprocess.Popen(args)
	# 		a.wait()
	# 
	# 	# Try to find matches between the current filename and items in the imaging session
	# 	match = os.path.basename(outfile.split(".")[0].strip().lower())
	# 	matches = idmap[match]
	# 
	# 	if len(idmap[match]) == 0:
	# 		print "Could not find micrograph for %s -- creating new micrograph."%match
	# 
	# 		mrec = {}
	# 		mrec["name"] = -1
	# 		mrec["rectype"] = "micrograph"
	# 		mrec["parents"] = [self.name]
	# 		mrec["id_micrograph"] = match
	# 
	# 		newrecord = {}
	# 		newrecord["name"] = -2
	# 		newrecord["rectype"] = 'scan'
	# 		newrecord["parents"] = [-1]
	# 		newrecord.update(self.applyparams)
	# 
	# 		m = emdash.transport.NewRecordTransport(newrecord=mrec)
	# 		s = emdash.transport.UploadTransport(newrecord=newrecord, filename=outfile, param="file_binary_image")
	# 
	# 		sidecar = s.sidecar_read()
	# 		if sidecar:
	# 			print "This scan already appears to be uploaded! Check record ID %s"%sidecar.get('name')
	# 			return []
	# 
	# 		return [m, s]
	# 
	# 
	# 	elif len(idmap[match]) == 1:
	# 		matches = matches.pop()
	# 		print "Found match for %s: %s"%(match, matches)
	# 		newrecord = {}
	# 		newrecord["name"] = -1
	# 		newrecord["rectype"] = 'scan'
	# 		newrecord["parents"] = [matches]
	# 		newrecord.update(self.applyparams)
	# 
	# 		return [emdash.transport.UploadTransport(newrecord=newrecord, filename=outfile, param="file_binary_image")]
	# 
	# 
	# 	elif len(idmap[match]) > 1:
	# 		print "Ambiguous matches for %s: %s -- skipping"%(match, matches)
	# 		return []


if __name__ == "__main__":
	emen2.db.handlers.main(globals())
	

	
