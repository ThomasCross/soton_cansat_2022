
filename = '3d_plot_csv.csv';
M = readmatrix(filename);
M(1,:) = [];
alt = M(:, 1);
lat = M(:, 2);
lon = M(:, 3);
plot3(lat,lon,alt)
box on
ax = gca;
ax.ZGrid = 'on';
ax.XGrid = 'on';
ax.YGrid = 'on';
xlabel('Latitude (degrees North)') 
ylabel('Longitude (degrees West)') 
zlabel('Height (Meters)') 
