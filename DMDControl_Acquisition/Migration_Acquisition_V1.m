%% Upload pattern to DMD
imFile1 = fopen( 'mask_C.bmp' );
imData6 = fread( imFile1, inf, 'uchar' );
fclose( imFile1 );
L=LightCrafter();
t = tcpclient('192.168.7.2',21845,"Timeout",10);
L=LightCrafter();
L.setBMPImage( imData6, t )

%% Static Lines
%Make sure to balance out distance between positions, number of positions
%and the DMD/Acquisition time!

%Switch OFF Live
%Ensure shutter is OFF in the beginning

pos = {[2421.2, 2205.1], [-92, 2205.1]}; %First position is a dummy position to warm up the lamp!
NoOfTimePoints = inf; %In terms of number of timepoints (related to DMD Frequency)
dmdFreq = 15; %in seconds
dmdDuration = 1; %in seconds
acquireEvery = 60; %Frequency of acquiring the Trans image, every nth time point
acquireEvery_Fluo = 240; %Frequency of acquiring the Fluo image, every nth time point
expDmd = 50; %Exposure of DMD - do not need
expTrans = 400; %Exposure of Trans image
expFluo = 600; %Exposure of Fluorescence (ms)
filename = 'D:\Celine\20210507\Data';

MakeTimer(pos, NoOfTimePoints, dmdFreq, dmdDuration, acquireEvery, acquireEvery_Fluo, expDmd, expTrans, expFluo, filename);

%% Moving Lines
% Don't keep the distance between lines the same as 'movement factor'!!!
% Lines will appear to stay stationary in that case


pos = {[1546.2, -6153.5], [4074, -6153.5]}; %First position is a dummy position to warm up the lamp!
cellNo = 100000;
cellType = "Rpe1 Tiam";
passage = "P11";
medium = "DMEM F12 1% FBS";
NoOfTimePoints = inf; %In terms of number of timepoints (related to DMD Frequency)
dmdFreq = 15; %in seconds
dmdDuration = 1; %in seconds
acquireEvery = 60; %Frequency of acquiring the Trans image, every nth time point
moveEvery = 8;
keepStatic = 2160;
expDmd = 1000; %Exposure of DMD - do not need
expTrans = 400; %Exposure of Trans image
expFluo = 600; %Exposure of Fluorescence (ms)
dt = 1; %in pixels
filename = "D:\Celine\20210526\Data";

r = groot;
Monitors = r.MonitorPositions;
MonitorA = Monitors(2,:);
img = zeros(1140-28, 910);
hFig = figure(1);
hAx  = axes();
% set the figure to full screen
set(hFig,'units','pixels','position', MonitorA);
% set the axes to full screen
set(hAx,'Unit','normalized','Position', [0 0 1 1]);
% hide the toolbar
set(hFig,'menubar','none');
% to hide the title
set(hFig,'NumberTitle','off');
imgH = imshow(img);

MakeTimer_move(pos, NoOfTimePoints, dmdFreq, dmdDuration, acquireEvery, moveEvery,...
    keepStatic, expDmd, expTrans, expFluo, dt, imgH, cellNo, cellType, passage, medium, filename);

