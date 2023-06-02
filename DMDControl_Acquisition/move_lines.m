function img = move_lines(thickness, spacing, count, dt)
    %% DMD size
    DMDsize = [910,1140-28];
    h = DMDsize(1); % height
    w = DMDsize(2); % width
    % image half screen = 290 pixels
    f =h/2/290; % facteur de conversion pixel camÃ©ra --> pixel DMD
    %% paramÃ¨tres
    s = spacing; % distance entre les lignes
    e = round(thickness*f); %  Ã©paisseur des lignes, on veut que ce soit 50 pixel camÃ©ra
    %% code
    % crÃ©ation image de base
    nbl = ceil(h/s); % nombre de lignes
    img_even=zeros(nbl*s,DMDsize(2)); % image pour le calcul des lignes
    % positions des lignes
    for i=1:nbl
        y(i)=(i-1)*s+1;
        img_even(y(i):y(i)+e-1, :)=1;
    end
    % actualisation image
    img_even = circshift(img_even,-count*dt);
    img = img_even(1:h,:); % image Ã  projeter
%     imshow(img);
%     r = groot;
%     Monitors = r.MonitorPositions;
%     MonitorA = Monitors(1,:);
    
 end