function MakeTimer_move(pos, NoOfTimePoints, dmdFreq, dmdDuration, acquireEvery, moveEvery, keepStatic, expDmd, expTrans, expFluo, dt, imgH, cellNo, cellType, passage, medium, filename)
   t=timer;
   count = 0;   
   cnt_dmd = 1;
   currentFolder = pwd;
   assembly = NET.addAssembly([currentFolder,'\Interop.MMAppLib.dll']); % Necessary to be able to launch Metamorph
   obj = MMAppLib.UserCallClass();

   function initTimer = initTimer(src, event)
       %Make txt file with info in folder
        disp(strcat('Started at :', datestr(now)));
        mkdir(filename);
        mkdir(strcat(filename, '\DMD_Pattern'));
        for i=1:length(pos)
            mkdir(strcat(filename, '\Position', num2str(i), '_', num2str(pos{i})))
        end
        params = ["cellNo", "dmdFreq", "dmdDuration", "acquireEvery", "moveEvery", "keepStatic", "expDmd", "expTrans", "expFluo", "dt"];
        values = [cellNo, dmdFreq, dmdDuration, acquireEvery, moveEvery, keepStatic, expDmd, expTrans, expFluo, dt];
        cell_val = ["cellType", "Passage", "Medium"; cellType, passage, medium];
        k = [params; values];

        fileID = fopen(strcat(filename, '\meta.txt'), 'wt');
        fprintf(fileID, '%s = %6.0f\r\n', k);
        fprintf(fileID, '%s = %s\r\n', cell_val);
        fclose(fileID);
   end


   function timerCallback = timerCallback(src, event)
        tic
        disp(datestr(now))
        disp(count)
        
        if (count < keepStatic)
                disp(strcat(num2str(count), 'first'));
                img = move_lines(0, 1);
                set(imgH, 'CData', img);
                drawnow;
                imwrite(logical(img), strcat(filename, '\DMD_Pattern\mask.tif'), 'Compression', 'none', 'WriteMode', 'append')
            
        elseif (count >= keepStatic) && (mod(count, moveEvery) == 0)
                img = move_lines(cnt_dmd, dt);
                set(imgH, 'CData', img);
                drawnow;
                imwrite(logical(img), strcat(filename, '\DMD_Pattern\mask.tif'), 'Compression', 'none', 'WriteMode', 'append')
                cnt_dmd = cnt_dmd + 1;
        end
        
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
%             obj.SetMMVariable('Device.Illumination.Setting','DMD-GFP');
%             obj.SetMMVariable('Camera.Digital.Exposure', expDmd);
            for i=1:length(pos)
                a = pos{i};  
                obj.SetMMVariable('Device.Stage.XPosition', a(1)); 
                obj.SetMMVariable('Device.Stage.YPosition', a(2));
                disp(strcat('Acquired', num2str(a)));
                obj.RunJournal('C:\MM\app\mmproc\journals\s.jnl'); %disp('Aquire')  
                time = clock;
                img = imread('C:\TEMP\temp.tif');
                imwrite(img, strcat(filename, '\Position', num2str(i), '_', num2str(pos{i}), '\TransImage', ...
                num2str(count), '_', num2str(time(4)), '-', num2str(time(5)), '-', num2str(time(6)), '.tif'), 'WriteMode', 'append');
            end
            %Fluorescence 
%             obj.SetMMVariable('Device.Illumination.Setting', 'CY3');
%             obj.SetMMVariable('Camera.Digital.Exposure', expFluo);
% 
%             for i=1:length(pos)
%                 a = pos{i};  
%                 obj.SetMMVariable('Device.Stage.XPosition', a(1)); 
%                 obj.SetMMVariable('Device.Stage.YPosition', a(2));
%                 disp(strcat('Acquired', num2str(a)));
%                 obj.RunJournal('C:\MM\app\mmproc\journals\s.jnl'); %disp('Aquire')  
%                 time = clock;
%                 img = imread('C:\TEMP\temp.tif');
%                 imwrite(img, strcat(filename, '\Position', num2str(i), '_', num2str(pos{i}), '\FluoImage', ...
%                 num2str(count), '_', num2str(time(4)), '-', num2str(time(5)), '-', num2str(time(6)), '.tif'), 'WriteMode', 'append');
%            end
        end
        count = count + 1;
        toc
   end

   t.StartFcn = @initTimer;
   t.TimerFcn = @timerCallback;
   t.Period   = dmdFreq;
   t.TasksToExecute = NoOfTimePoints;
   t.ExecutionMode  = 'fixedRate';
   t.BusyMode = 'queue';
   start(t);
end
   
