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


;paths and filenames to static data
first_bolo_name = 'h1b1'  

wdir = '/home/domars/idlpro/aztec_idl_utilities/parameters_ASTE07/'
bstemplate = wdir+ 'bolostats_template.sav'
bolostats_file = wdir+'bolostats_default.txt'
blisttemplate = wdir+'bololist_template.sav'
blist_file = wdir+'bololist.csv'
bdc2tausave = wdir+'fit_parameters_bolodc2tau_ASTE07.sav'
bdc2ressave = wdir+'fit_parameters_bolodc2responsivity_ASTE07.sav'

;the following loops through all ASTE datafiles and generates a
;bolostats.xml file for each datafile.


;loop on files
raw_file_dir = '/home/domars/tesis/aztec_c++/sample_files/test/RXJ1347/raw_data/'
cd, raw_file_dir
a = file_search('*.nc')
nfiles = n_elements(a)

for j=0,nfiles-1 do begin
   filename = a[j]
   outxml = repstr(filename,'.nc','.bstats')

   ;use the aztec utility to get the beammap parameters
   bs = aztec_aste_get_beammap_params(filename)

   ;grab up the file's bolo names and make a new id while we are here
   ncfid = ncdf_open(filename)
   varid_h1b1 = ncdf_varid(ncfid, first_bolo_name)
   bolonames = strarr(144)
   boloid = strarr(144)
   bolo_ncdf_location = intarr(144)
   for i=0,143 do begin
      t = ncdf_varinq(ncfid,varid_h1b1+i)
      bolonames[i] = t.name
      boloid[i] = strcompress('d'+string(i),/rem)
      bolo_ncdf_location[i] = varid_h1b1+i
   endfor
   ncdf_close, ncfid

   ;figure out the goodflag from the location of NaNs
   goodflag = intarr(n_elements(bs.boloname))+1
   goodflag[where(finite(bs.az_fwhm) eq 0)] = 0
   
   ;now update the goodflag by getting the values from bololist.csv
   restore, blisttemplate
   bl = read_ascii(blist_file, template=template)
   goodflag[where(bl.newgf eq 0)] = 0

   ;get offsets, slopes and errors for bolodc to tau conversion
   restore, bdc2tausave
   offset_dc2tau = offset
   slope_dc2tau = slope
   offset_err_dc2tau = offset_err
   slope_err_dc2tau = slope_err

   ;get offsets, slopes and errors for bolodc to responsivity conversion
   restore, bdc2ressave
   offset_dc2res = offset
   slope_dc2res = slope
   offset_err_dc2res = offset_err
   slope_err_dc2res = slope_err

   ;now the output xml
   openw, 6, outxml
   npts = n_elements(bs.boloname)
   printxmlvar, 6, 'nBolos', 144
   for i=0,npts-1 do begin
      printf, 6, strcompress('<'+boloid[i]+'>',/rem)
      printxmlvar, 6, 'name', bolonames[i]
      printxmlvar, 6, 'ncdf_location', bolo_ncdf_location[i]
      printxmlvar, 6, 'az_fwhm', bs.az_fwhm[i], units='arcseconds'
      printxmlvar, 6, 'el_fwhm', bs.el_fwhm[i], units='arcseconds'
      printxmlvar, 6, 'az_offset', bs.az_offset[i], units='arcseconds'
      printxmlvar, 6, 'el_offset', bs.el_offset[i], units='arcseconds'
      printxmlvar, 6, 'bologain', bs.bologain[i], units='mJy/nW'
      printxmlvar, 6, 'bologain_err', bs.bologain_err[i], units='mJy/nW'
      printxmlvar, 6, 'bolosens', bs.bolosens[i], units='mJy-rt(s)'
      printxmlvar, 6, 'offset_dc2tau',offset_dc2tau[i]
      printxmlvar, 6, 'offset_err_dc2tau', offset_err_dc2tau[i]
      printxmlvar, 6, 'slope_dc2tau', slope_dc2tau[i]
      printxmlvar, 6, 'slope_err_dc2tau', slope_err_dc2tau[i]
      printxmlvar, 6, 'offset_dc2responsivity',offset_dc2res[i]
      printxmlvar, 6, 'offset_err_dc2responsivity', offset_err_dc2res[i]
      printxmlvar, 6, 'slope_dc2responsivity', slope_dc2res[i]
      printxmlvar, 6, 'slope_err_dc2responsivity', slope_err_dc2res[i]
      printxmlvar, 6, 'quad_dc2tau', 0.0
      printxmlvar, 6, '	quad_err_dc2tau', 0.0
      printxmlvar, 6, 'goodflag', goodflag[i]
      printf, 6, strcompress('</'+boloid[i]+'>',/rem)
   endfor
   close, 6
endfor

end





