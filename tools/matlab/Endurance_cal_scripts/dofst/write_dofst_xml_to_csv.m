function write_dofst_xml_to_csv(xmlfilename)
%.. desiderio 01-oct-2017
% (For McLane profilers, CE09OSPM).
%
%.. reads in the Seabird 43F O2 xmlfile and writes out the SBE-equation
%.. calcoeffs to a csv file to upload to the calibrations folder in the 
%.. assetManagement GitHub repository.

%***********************************************************************
%***********************************************************************
%***********************************************************************
%         USE SOC ***ADJUSTED***
%         which may or may not be the Soc value in the xml file;
%
%         CHECK THE ENTRY IN THE PDF WHICH SHOULD READ:
%         Soc = [value] (adj)    
%***********************************************************************
%***********************************************************************
%***********************************************************************

%.. filename must include the full path of the xmlfile unless
%.. the file is located in the working directory.

%.. so that SBE caldate can be parsed into yyyymmdd format:
months = {'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', ...
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'};

caldate_provenance = 'date in filename comes from Soc-adjusted caldate';
Soc_type = 'this is the adjusted Soc (O2 signal slope) value';

%.. set up notes character strings for write-out loop
notes = {caldate_provenance,  ...
         Soc_type,            ...
         '',                  ...
         '',                  ...
         '',                  ...
         ''                   };
%.. CI calcoeff names to write out to the csv file.
csvVarName = {'CC_frequency_offset' ...
              'CC_oxygen_signal_slope' ...
              'CC_residual_temperature_correction_factor_a' ...
              'CC_residual_temperature_correction_factor_b' ...
              'CC_residual_temperature_correction_factor_c' ...
              'CC_residual_temperature_correction_factor_e'};

%.. coefficient names in the xml file. for coding simplicity, parse
%.. in the same order as in csvVarName, and for completeness also
%.. parse for those calcoeffs that are not currently archived by
%.. OOI CI (which are the 'dynamic' calcoeffs related to tau, the
%.. time response of the O2 sensor).
xmlVarName = {'offset', 'Soc', 'A', 'B', 'C', 'E',   ...
              'D0', 'D1', 'D2', 'Tau20', 'H1', 'H2', 'H3'};
              
fid = fopen(xmlfilename);
%.. read in all lines. make sure there is no 'holdover' cell
clear C
C = textscan(fid, '%s', 'whitespace', '', 'delimiter', '\n');
fclose(fid);
%.. get rid of wrapping cell array
C = C{1};

%.. parse serial number into con structure variable
idx_sn = find(~cellfun(@isempty, strfind(C,'<SerialNumber>')), 1);
str = C{idx_sn};
idx_ket = strfind(str, '>');  % two of these in this xml line
idx_bra = strfind(str, '<');  % two of these in this xml line
idx_range = (idx_ket(1)+1):(idx_bra(2)-1);
con.sernum = sscanf(str(idx_range), '%u');

%.. parse calibration date into con structure variable
idx_sn = find(~cellfun(@isempty, strfind(C,'<CalibrationDate>')), 1);
str = C{idx_sn};
idx_ket = strfind(str, '>');  % two of these in this xml line
idx_bra = strfind(str, '<');  % two of these in this xml line
idx_range = (idx_ket(1)+1):(idx_bra(2)-1);
caldate = sscanf(str(idx_range), '%s');    % dd-mmm-yy
mm = find(strcmpi(months, caldate(4:6)));  % get month number
con.caldate = strcat('20', caldate(8:9), num2str(mm, '%2.2u'), ...
                     caldate(1:2));        % yyyymmdd

%.. parse the SBE equation calcoeffs into con structure variable
%.. note that parsing string fields using sscanf '%s' is effective
%.. as a strtrim mechanism
%.. .. delete the Owens-Millard section, which shares calcoeff names
match0 = 'CalibrationCoefficients equation="0"';
idx_OM_eqn  = find(~cellfun(@isempty, strfind(C,match0)), 1);
match1 = 'CalibrationCoefficients equation="1"';
idx_SBE_eqn = find(~cellfun(@isempty, strfind(C,match1)), 1);
C(idx_OM_eqn:idx_SBE_eqn-1) = [];
%.. .. iterate through xmlVarName
for ii=1:length(xmlVarName)
    idx = find(~cellfun(@isempty, strfind(C,['<' xmlVarName{ii} '>'])), 1);
    if isempty(idx)
        con.(xmlVarName{ii}) = '';
        continue
    end 
    str = C{idx};
    idx_ket = strfind(str, '>');  % two of these in this xml line
    idx_bra = strfind(str, '<');  % two of these in this xml line
    idx_range = (idx_ket(1)+1):(idx_bra(2)-1);
    con.(xmlVarName{ii}) = sscanf(str(idx_range), '%s');
end

%.. construct outfile name
sernum = num2str(con.sernum, '%5.5u');
csvfilename = ['CGINS-DOFSTK-' sernum '__' con.caldate '.csv'];

%.. serial number string for calfile entries
sernum = ['43-' num2str(con.sernum)];
fid = fopen(csvfilename, 'w');
header = 'serial,name,value,notes';
fprintf(fid, '%s\r\n', header);
for ii = 1:length(csvVarName)
    fprintf(fid, '%s,%s,%s,%s\r\n', ...
        sernum, csvVarName{ii}, con.(xmlVarName{ii}), notes{ii});
end
fclose(fid);

