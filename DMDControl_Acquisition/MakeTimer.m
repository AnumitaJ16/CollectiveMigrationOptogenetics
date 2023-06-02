function MakeTimer(pos, pos_cont, NoOfTimePoints, dmdFreq, dmdDuration, acquireEvery, acquireCont, acquireEvery_Fluo, expDmd, expTrans, expFluo, cellNo, cellType, passage, medium, filename)
   t=timer;
   count = 0;
   currentFolder = pwd;
   assembly = NET.addAssembly([currentFolder,'\Interop.MMAppLib.dll']); % Necessary to be able to launch Metamorph
   obj = MMAppLib.UserCallClass();

   function initTimer = initTimer(src, event)
       %Make txt file with info in folder
        disp(strcat('Started at :', datestr(now)));
        mkdir(filename); 
        for i=1:length(pos)
            mkdir(strcat(filename, '\Position', num2str(i), '_', num2str(pos{i})))
        end
        for i=1:length(pos_cont)
            mkdir(strcat(filename, '\Control_Position', num2str(i), '_', num2str(pos_cont{i})))
        end
        params = ["cellNo", "dmdFreq", "dmdDuration", "acquireEvery", "expDmd", "expTrans", "expFluo"];
        values = [cellNo, dmdFreq, dmdDuration, acquireEvery, expDmd, expTrans, expFluo];
        cell_val = ["cellType", "Passage", "Medium"; cellType, passage, medium];
        k = [params; values];

        fileID = fopen(strcat(filename, '\meta.txt'), 'wt');
        fprintf(fileID, '%s = %6.0f\r\n', k);
        fprintf(fileID, '%s = %s\r\n', cell_val);
        fclose(fileID);
   end

   function timerCallback = timerCallback(src, event)
       disp(datestr(now));
       disp(count);
            for i=1:length(pos)
                obj.SetMMVariable('Device.Illumination.Setting','DMD-GFP');
                obj.SetMMVariable('Camera.Digital.Exposure', expDmd);
                a = pos{i};
                disp(strcat('moved to pos :', num2str(a)));
                obj.SetMMVariable('Device.Stage.XPosition', a(1)); 
                obj.SetMMVariable('Device.Stage.YPosition', a(2));
                 %disp(strcat('Illuminated here', num2str(a)));
                obj.RunJournal('C:\MM\app\mmproc\journals\Shutter.jnl'); %disp('Shine light');
                pause(dmdDuration)
                obj.RunJournal('C:\MM\app\mmproc\journals\Shutter.jnl'); %disp('done');
            end
            
            if mod(count, acquireEvery) == 0 
                obj.SetMMVariable('Device.Illumination.Setting','TRANS');
                obj.SetMMVariable('Camera.Digital.Exposure', expTrans);
                for i=1:length(pos)
                    a = pos{i};  
                    obj.SetMMVariable('Device.Stage.XPosition', a(1)); 
                    obj.SetMMVariable('Device.Stage.YPosition', a(2));
                    disp(strcat('Acquired Trans', num2str(a)));
                    obj.RunJournal('C:\MM\app\mmproc\journals\s.jnl'); %disp('Aquire')  
                    time = clock;
                    img = imread('C:\TEMP\temp.tif');
                    imwrite(img, strcat(filename, '\Position', num2str(i), '_', num2str(pos{i}), '\TransImage', ...
                    num2str(count), '_', num2str(time(4)), '-', num2str(time(5)), '-', num2str(time(6)), '.tif'), 'WriteMode', 'append');
                end
            end
            
            if mod(count, acquireCont) == 0 
                obj.SetMMVariable('Device.Illumination.Setting','TRANS');
                obj.SetMMVariable('Camera.Digital.Exposure', expTrans);
                for i=1:length(pos_cont)
                    a = pos_cont{i};  
                    obj.SetMMVariable('Device.Stage.XPosition', a(1)); 
                    obj.SetMMVariable('Device.Stage.YPosition', a(2));
                    disp(strcat('Acquired Control: ', num2str(a)));
                    obj.RunJournal('C:\MM\app\mmproc\journals\s.jnl'); %disp('Aquire')  
                    time = clock;
                    img = imread('C:\TEMP\temp.tif');
                    imwrite(img, strcat(filename, '\Control_Position', num2str(i), '_', num2str(pos_cont{i}), '\ContTransImage', ...
                    num2str(count), '_', num2str(time(4)), '-', num2str(time(5)), '-', num2str(time(6)), '.tif'), 'WriteMode', 'append');
                end

            end
%             %Fluorescence 
%             if mod(count, acquireEvery_Fluo) == 0 
%                 obj.SetMMVariable('Device.Illumination.Setting', 'CY3_2');
%                 obj.SetMMVariable('Camera.Digital.Exposure', expFluo);
% 
%                 for i=1:length(pos)
%                     a = pos{i};  
%                     obj.SetMMVariable('Device.Stage.XPosition', a(1)); 
%                     obj.SetMMVariable('Device.Stage.YPosition', a(2));
%                     disp(strcat('Acquired Fluo', num2str(a)));
%                     obj.RunJournal('C:\MM\app\mmproc\journals\s.jnl'); %disp('Aquire')  
%                     time = clock;
%                     img = imread('C:\TEMP\temp.tif');
%                     imwrite(img, strcat(filename, '\Position', num2str(i), '_', num2str(pos{i}), '\FluoImage', ...
%                     num2str(count), '_', num2str(time(4)), '-', num2str(time(5)), '-', num2str(time(6)), '.tif'), 'WriteMode', 'append');
%                 end
% 
%             end
            count = count + 1;  
   end

   t.StartFcn = @initTimer;
   t.TimerFcn = @timerCallback;
   t.Period   = dmdFreq;
   t.TasksToExecute = NoOfTimePoints;
   t.ExecutionMode  = 'fixedRate';
   t.BusyMode = 'queue';
   start(t);
end
   
