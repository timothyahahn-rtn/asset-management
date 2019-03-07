function [con] = rad_read_ctdbp_cap(capfilename)
%.. desiderio 30-sep-2017
%.. .. rad_read_ctdbp_cap operates on captured files from a SBE16+ CTD.
%.. .. created by modifying rad_read_presf_cap.m (SBE26+)
%
%.. reads in calcoeffs from Seabird 16+ text files into the output
%.. structure cal. Input files are 'cap' (captured) files from a QCT.
%..
%.. the cal information in the SBE16+ hex file header is in an xml
%.. format, so that if calcoeffs are to be read from a hex file,
%.. the script rad_read_ctdbp_xmlcon.m may work.
%
%.. filename must include the full path of the infile unless
%.. the file is located in the working directory.
%
%.. cal coefficient names as read from the cap file.
%.. the first 4 names are A0, A1, A2, and A3 in the xmlcon files
%..     and in the pdf documentation.
coeff_name = {'TA0', 'TA1', 'TA2', 'TA3',      ...
              'PTEMPA0', 'PTEMPA1', 'PTEMPA2', ...
              'PTCA0', 'PTCA1', 'PTCA2',       ...
              'PTCB0', 'PTCB1', 'PTCB2',       ...
              'PA0', 'PA1', 'PA2',             ...
              'G', 'H', 'I', 'J', 'CPCOR', 'CTCOR' };

%.. field names will follow xmlcon and pdf convention.
field_name = {'A0', 'A1', 'A2', 'A3',      ...
              'PTEMPA0', 'PTEMPA1', 'PTEMPA2', ...
              'PTCA0', 'PTCA1', 'PTCA2',       ...
              'PTCB0', 'PTCB1', 'PTCB2',       ...
              'PA0', 'PA1', 'PA2',             ...
              'G', 'H', 'I', 'J', 'CPCOR', 'CTCOR' };

fid = fopen(capfilename);
%.. read in all lines.
C = textscan(fid, '%s', 'whitespace', '', 'delimiter', '\n');
fclose(fid);
%.. get rid of wrapping cell array
C = C{1};

%.. parse serial number into cal data structure.
idx = find(~cellfun(@isempty, strfind(C, 'SERIAL NO.')), 1);
if isempty(idx)
    error('Could not find serial number');
end
str = C{idx};
%.. read serial number from characters after 'NO.' 
idx = strfind(str, 'NO.');
con.sernum = sscanf(str(idx+4:idx+8), '%u');

%.. find the temperature sensor caldate
match = 'temperature: ';
idx = find(~cellfun(@isempty, strfind(C, match)), 1);
if isempty(idx)
    error('Could not find Temperature coefficients');
end
str = C{idx};
%.. read caldate from characters after ':'
idx = strfind(str, ':');
con.caldate_temperature = str(idx+3:idx+11);

%.. find the conductivity sensor caldate
match = 'conductivity: ';
idx = find(~cellfun(@isempty, strfind(C, match)), 1);
if isempty(idx)
    error('Could not find Conductivity coefficients');
end
str = C{idx};
%.. read caldate from characters after ':'
idx = strfind(str, ':');
con.caldate_conductivity = str(idx+3:idx+11);

%.. find the pressure sensor caldate
match = 'pressure S/N = ';
idx = find(~cellfun(@isempty, strfind(C, match)), 1);
if isempty(idx)
    error('Could not find Pressure coefficients');
end
str = C{idx};
%.. read caldate from characters after ':'
idx = strfind(str, ':');
con.caldate_pressure = str(idx+3:idx+11);

%.. populate the structure fields
%.. prepend a space to coeff_name in the strfind statement so that
%.. 'PA# = ' can be differentiated from 'PTEMPA# = ', #=1,2,3
for ii=1:length(coeff_name)
    idx = find(~cellfun(@isempty, strfind(C,[' ' coeff_name{ii} ' = '])));
    if isempty(idx)
        con.(coeff_name{ii}) = '';
    else
        %.. some of the cap files have coeffs written out twice;
        %.. just in case they could have been changed during the
        %.. SBE procedure, use last one.
        str = C{idx(end)};
        idx_eq = strfind(str, '=');
        con.(field_name{ii}) = str(idx_eq+2:end);
    end
end

clear C
