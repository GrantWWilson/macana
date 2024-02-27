
;aztec_ancillary_data_to_xml.pro
;this is a utility to take a netcdf file and its associated bolostats
;and goodflag files and reformat all key information into an xml file

;xml formatter
;change units to optional input
pro printxmlvar, lun, varname, value, units=units
  printf, lun, '  '+strcompress('<'+varname+'>',/rem)
  if(keyword_set(units)) then begin
     printf, lun, '    <value>'+strcompress(string(value),/rem)+'</value>'+$
                      '<units>'+strcompress(units)+'</units>'
  endif else begin
     printf, lun, '    <value>'+strcompress(string(value),/rem)+'</value>'
  endelse
  printf, lun, '  '+strcompress('</'+varname+'>',/rem)
end


;working dir
working_dir = '/data/wilson/LMT_ES3/GUTR001/Field01/raw_data/'
cd, working_dir

;collect files to use
ncdf_file = findfile('aztec*.nc')
outfile = repstr(ncdf_file,'.nc','.bstats')
nfiles = n_elements(ncdf_file)

;set up some filenames and constants
first_bolo_name = 'Data.AztecBackend.h1b1'
bstemplate = '/home/wilson/aztec_idl_utilities/parameters_LMTES3/bolostats_template.sav'
bolostats_file = '/home/wilson/aztec_idl_utilities/parameters_LMTES3/bolostats_default.txt'
blisttemplate = '/home/wilson/aztec_idl_utilities/parameters_LMTES3/bololist_template.sav'
blist_file = '/home/wilson/aztec_idl_utilities/parameters_LMTES3/bololist.csv'
bdc2tausave = '/home/wilson/aztec_idl_utilities/parameters_LMTES3/fit_parameters_bolodc2tau_LMTES3.sav'
bdc2ressave = '/home/wilson/aztec_idl_utilities/parameters_LMTES3/fit_parameters_bolodc2responsivity_LMTES3.sav'

for i=0,nfiles-1 do begin
   ncfid = ncdf_open(ncdf_file[i])
   varid_h1b1 = ncdf_varid(ncfid, first_bolo_name)
   ;grab up the file's bolo names and make a new id while we are here
   bolonames = strarr(144)
   boloid = strarr(144)
   bolo_ncdf_location = intarr(144)
   for j=0,143 do begin
      t = ncdf_varinq(ncfid,varid_h1b1+j)
      bolonames[j] = t.name
      boloid[j] = strcompress('d'+string(j),/rem)
      bolo_ncdf_location[j] = varid_h1b1+j
   endfor
   ncdf_close, ncfid

   ;read in the bolostats file
   restore, bstemplate
   bs = read_ascii(bolostats_file,template=bolostats_template)

   ;figure out the goodflag from the location of NaNs
   goodflag = intarr(n_elements(bs.boloname))+1
   goodflag[where(finite(bs.az_fwhm) eq 0)] = 0

   ;now update the goodflag by getting the values from bololist.csv
   restore, blisttemplate
   bl = read_ascii(blist_file, template=template)
   goodflag[where(bl.newgf eq 0)] = 0
   
   ;get offsets, slopes and errors for bolodc to tau conversion
   restore, bdc2tausave
   if(not keyword_set(p0)) then begin
      offset_dc2tau = offset
      slope_dc2tau = slope
      quad_dc2tau = dblarr(n_e(offset))
      offset_err_dc2tau = offset_err
      slope_err_dc2tau = slope_err
      quad_err_dc2tau = dblarr(n_e(offset))
   endif else begin
      offset_dc2tau = p0
      slope_dc2tau = p1
      quad_dc2tau = p2
      offset_err_dc2tau = p0_err
      slope_err_dc2tau = p1_err
      quad_err_dc2tau = p2_err
   endelse      
      

   ;get offsets, slopes and errors for bolodc to responsivity conversion
   restore, bdc2ressave
   offset_dc2res = offset
   slope_dc2res = slope
   offset_err_dc2res = offset_err
   slope_err_dc2res = slope_err
   
   ;get the gain, az and el offsets and az and el fwhm using the utility
   offinfo = aztec_lmt_get_beammap_params(ncdf_file[i])
   
   ;now the output xml
   openw, 6, outfile[i]
   npts = n_elements(bs.boloname)
   printxmlvar, 6, 'nBolos', 144
   for j=0,npts-1 do begin
      printf, 6, strcompress('<'+boloid[j]+'>',/rem)
      printxmlvar, 6, 'name', bolonames[j]
      printxmlvar, 6, 'ncdf_location', bolo_ncdf_location[j]
      printxmlvar, 6, 'az_fwhm', offinfo.az_fwhm[j], units='arcseconds'
      printxmlvar, 6, 'el_fwhm', offinfo.el_fwhm[j], units='arcseconds'
      printxmlvar, 6, 'az_offset', offinfo.az_offset[j], units='arcseconds'
      printxmlvar, 6, 'el_offset', offinfo.el_offset[j], units='arcseconds'
      printxmlvar, 6, 'bologain', offinfo.bologain[j], units='mJy/nW'
      printxmlvar, 6, 'bologain_err', offinfo.bologain_err[j], units='mJy/nW'
      printxmlvar, 6, 'bolosens', offinfo.bolosens[j], units='mJy-rt(s)'
      printxmlvar, 6, 'offset_dc2tau',offset_dc2tau[j]
      printxmlvar, 6, 'offset_err_dc2tau', offset_err_dc2tau[j]
      printxmlvar, 6, 'slope_dc2tau', slope_dc2tau[j]
      printxmlvar, 6, 'slope_err_dc2tau', slope_err_dc2tau[j]
      printxmlvar, 6, 'quad_dc2tau', quad_dc2tau[j]
      printxmlvar, 6, 'quad_err_dc2tau', quad_err_dc2tau[j]
      printxmlvar, 6, 'offset_dc2responsivity',offset_dc2res[j]
      printxmlvar, 6, 'offset_err_dc2responsivity', offset_err_dc2res[j]
      printxmlvar, 6, 'slope_dc2responsivity', slope_dc2res[j]
      printxmlvar, 6, 'slope_err_dc2responsivity', slope_err_dc2res[j]
      printxmlvar, 6, 'goodflag', goodflag[j]
      printf, 6, strcompress('</'+boloid[j]+'>',/rem)
   endfor
   close, 6
endfor

end
