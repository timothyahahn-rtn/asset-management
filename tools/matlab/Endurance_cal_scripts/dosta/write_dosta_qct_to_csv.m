function csvfilename = write_dosta_qct_to_csv(qct)
%.. desiderio 06-apr-2017
%
% APPEND CAL DATE FROM PDF TO QCT FILENAME: YYYYMMDD
%
%.. reads in a DOSTA QCT which has been renamed by appending the
%.. calibration certificate's caldate to the filename and outputs
%.. a csv file to be uploaded to a calibration folder on the
%.. ooi-integration GitHub repository.

seriesD = [134:136 217:223 291 292 313:315 477:480 482:485]; 
seriesJ = [209 308 350:353 646 672];  % 350 and 351 are whoi's

caldate_provenance = ['date in filename comes from ' ...
                      'factory calibration certificate'];
clear C D

fid = fopen(qct);
%.. read in all lines.
C = textscan(fid, '%s', 'whitespace', '', 'delimiter', '\n');
fclose(fid);
%.. get rid of wrapping cell array
C = C{1};

%.. parse serial number
idx = find(~cellfun(@isempty, strfind(C,'Serial Number')), 1);
D = textscan(C{idx}, '%s', 'whitespace', ' ', 'delimiter', '\t');
D=D{1};    % undo wrapping
sernum = D{4};
sernum_check = D{3};
if ~strcmp(sernum, sernum_check)
    error('Serial number values within QCT do not agree.');
end

%.. find series based on serial number
sernum = str2double(sernum);
if ismember(sernum, seriesD)
    series = 'D';
elseif ismember(sernum, seriesJ)
    series = 'J';
else
    error('DOSTA Series cannot be determined from serial number.');
end

%.. now convert serial number to 5 characters;
%.. this will work if serialnumbers > 999
sn_str = num2str(sernum, '%5.5u');

%.. find date of cal; this should have been appended 
%.. to the QCT infilename
[~, name, ~] = fileparts(qct);
caldate = name(end-7:end);  % expect yyyymmdd
if ~strcmp(caldate(1:2), '20')
    error('Was caldate appended to QCT filename?');
end

%.. parse for so-called concentration coefficients
idx = find(~cellfun(@isempty, strfind(C,'ConcCoef')), 1);
D = textscan(C{idx}, '%s', 'whitespace', ' ', 'delimiter', '\t');
D=D{1};    % undo wrapping
offset = D{4};
slope  = D{5};

%.. parse for SVU (multipoint calibration) coefficients
idx = find(~cellfun(@isempty, strfind(C,'SVUFoilCoef')), 1);
D = textscan(C{idx}, '%s', 'whitespace', ' ', 'delimiter', '\t');
D = D{1};     % undo wrapping
D(1:3) = [];  % delete non-SVU elements

%.. construct output filename
csvfilename = ['CGINS-DOSTA' series '-' sn_str '__' caldate '.csv'];

%.. write directly out to a text file, no xlsx in-between.
fid = fopen(csvfilename, 'w');
header = 'serial,name,value,notes';
fprintf(fid, '%s\r\n', header);
cc_array = ['[' offset ', ' slope ']'];
fprintf(fid, '%i,%s,"%s",%s\r\n', ...
    sernum, 'CC_conc_coef',cc_array,caldate_provenance);
%.. construct character array containing svu coeffs
svu_array = '[';
for ii = 1:length(D)
    svu_array = [svu_array D{ii} ', '];
end
svu_array(end-1:end) = [];
svu_array(end+1) = ']';
%.. and export
fprintf(fid, '%i,%s,"%s",\r\n', ...
    sernum, 'CC_csv',svu_array);

fclose(fid);


end
