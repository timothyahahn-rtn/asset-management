function write_flort_qct_to_csv(qct)
%.. desiderio 07-apr-2017
%.. desiderio 18-oct-2017 removed 'BBFL2W-' from serial numbers 
%..                       in 1st column of calfile.
%.. desiderio 28-nov-2017 seriesJ serial numbers WILL use 'BBFL2W-'

%*********************************************
% APPEND CALDATE TO FILENAME:  YYYYMMDD
%*********************************************
%
%.. reads in a FLORT QCT which has been renamed by appending the
%.. calibration file's caldate to the filename and outputs
%.. a csv file to be uploaded to a calibration folder on the
%.. ooi-integration GitHub repository.

% cd R:
% cd ..

seriesD = [ 995  996 1121 1123   1151 1152 1153 1154  ...
           1155 1197 1290 1291   1302 1303 1487 1488]; 
seriesJ = [1084 1156 1206 1207   1518 1519];

caldate_provenance = ['date in filename comes from ' ...
                      'factory characterization sheet'];

%.. the coefficient called 'angular resolution' *isn't* 
bug = ['Erroneously named constant; this coefficient scales the ' ...
    'particulate scattering at 124 degrees to total backscatter ' ...
    'from particles'];

clear C D

str_dark  = {'M1d' 'M2d' 'M3d'};
str_scale = {'M1s' 'M2s' 'M3s'};


fid = fopen(qct);
%.. read in all lines.
C = textscan(fid, '%s', 'whitespace', '', 'delimiter', '\n');
fclose(fid);
%.. get rid of wrapping cell array
C = C{1};

%.. parse serial number
idx = find(~cellfun(@isempty, strfind(C,'Ser BBFL2W')), 1);
D = textscan(C{idx}, '%s%f', 'whitespace', ' ', 'delimiter', '-');
sernum = D{2};

%.. find series based on serial number
if ismember(sernum, seriesD)
    series = 'D';
elseif ismember(sernum, seriesJ)
    series = 'J';
else
    error('FLORT Series cannot be determined from serial number.');
end

%.. now convert serial number to 5 characters for calfilename
sn_str = num2str(sernum, '%5.5u');

%.. find date of cal; this should have been appended 
%.. to the QCT infilename
[~, name, ~] = fileparts(qct);
caldate = name(end-7:end);  % expect yyyymmdd

%.. parse for dark counts and scale factor values
darkcounts = nan(1,3);
scalefactor = nan(1,3);
for ii=1:3
    idx = find(~cellfun(@isempty, strfind(C,str_dark{ii})), 1);
    D = textscan(C{idx}, '%s%f', 'delimiter', ' ');
    darkcounts(ii) = D{2}; 
    idx = find(~cellfun(@isempty, strfind(C,str_scale{ii})), 1);
    D = textscan(C{idx}, '%s%f', 'delimiter', ' ');
    scalefactor(ii) = D{2};
end

%.. construct output filename
csvfilename = ['CGINS-FLORT' series '-' sn_str '__' caldate '.csv'];

%.. construct serial number string to be into column 1 of calfile
if strcmpi(series, 'J')
    sn_str = ['BBFL2W-' num2str(sernum)];
else
    sn_str = num2str(sernum);
end

%.. write directly out to a text file, no xlsx in-between.
fid = fopen(csvfilename, 'w');
header = 'serial,name,value,notes';
fprintf(fid, '%s\r\n', header);

fprintf(fid, '%s,%s,%g,%s\r\n', ...
    sn_str, 'CC_dark_counts_cdom', darkcounts(3), caldate_provenance);
fprintf(fid, '%s,%s,%g,\r\n', ...
    sn_str, 'CC_scale_factor_cdom', scalefactor(3));
fprintf(fid, '%s,%s,%g,\r\n', ...
    sn_str, 'CC_dark_counts_chlorophyll_a', darkcounts(2));
fprintf(fid, '%s,%s,%g,\r\n', ...
    sn_str, 'CC_scale_factor_chlorophyll_a', scalefactor(2));
fprintf(fid, '%s,%s,%g,\r\n', ...
    sn_str, 'CC_dark_counts_volume_scatter', darkcounts(1));
fprintf(fid, '%s,%s,%g,\r\n', ...
    sn_str, 'CC_scale_factor_volume_scatter', scalefactor(1));
fprintf(fid, '%s,%s,%s,%s\r\n', ...
    sn_str, 'CC_depolarization_ratio', '0.039', 'Constant');
fprintf(fid, '%s,%s,%s,%s\r\n', ...
    sn_str, 'CC_measurement_wavelength', '700', '[nm]; Constant');
fprintf(fid, '%s,%s,%s,%s\r\n', ...
    sn_str, 'CC_scattering_angle', '124', '[degrees]; Constant');
fprintf(fid, '%s,%s,%s,%s\r\n', ...
    sn_str, 'CC_angular_resolution', '1.076', bug);

fclose(fid);


end
