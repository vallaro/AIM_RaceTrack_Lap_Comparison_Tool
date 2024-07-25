import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from shapely.geometry import LineString

def read_gps_data(file_path):
    # Laadi andmed ja valmista need ette
    gps_data = pd.read_csv(file_path, skiprows=14)
    
    # Eemalda ühikute rida ja lähtesta indeks
    gps_data = gps_data.drop(0).reset_index(drop=True)
    
    # Muuda vastavad veerud numbrilisteks tüüpideks
    numeric_columns = [
        "Time", "GPS Speed", "GPS Nsat", "GPS LatAcc", "GPS LonAcc", "GPS Slope", 
        "GPS Heading", "GPS Gyro", "GPS Altitude", "GPS PosAccuracy", 
        "GPS SpdAccuracy", "GPS Radius", "GPS Latitude", "GPS Longitude", 
        "External Voltage", "Exhaust Temp", "Internal Battery", "RPM"
    ]
    gps_data[numeric_columns] = gps_data[numeric_columns].apply(pd.to_numeric, errors='coerce')
    
    return gps_data

def process_laps(gps_data, start_finish_line_geom):
    laps = 0
    crosses = [laps]
    start_indices = [0]
    
    # Kontrolli iga segmenti, kas see ületab start/finish joont
    for i in range(1, len(gps_data)):
        if segment_crosses_line(
            gps_data.iloc[i-1]['GPS Longitude'], gps_data.iloc[i-1]['GPS Latitude'],
            gps_data.iloc[i]['GPS Longitude'], gps_data.iloc[i]['GPS Latitude'],
            start_finish_line_geom
        ):
            laps += 1
            start_indices.append(i)
        crosses.append(laps)
    
    # Lisa ringi andmed DataFrame'i
    gps_data['Lap'] = crosses[:len(gps_data)]
    
    return gps_data, start_indices

def segment_crosses_line(lon1, lat1, lon2, lat2, line_geom):
    return LineString([(lon1, lat1), (lon2, lat2)]).crosses(line_geom)

# Failide teed
file_path_1 = 'data1.csv'
file_path_2 = 'data2.csv'

# Laadi andmed kahest failist
gps_data_1 = read_gps_data(file_path_1)
gps_data_2 = read_gps_data(file_path_2)

# Määratle start/finish joon koordinaatidega
start_finish_line_geom = LineString([
    (25.746169, 59.124332),
    (25.746008, 59.124303)
])

# Töötle ringide andmed
gps_data_1, start_indices_1 = process_laps(gps_data_1, start_finish_line_geom)
gps_data_2, start_indices_2 = process_laps(gps_data_2, start_finish_line_geom)

# Funktsioon ringi kestvuse arvutamiseks
def calculate_lap_times(gps_data, start_indices):
    lap_times = []
    for i in range(1, len(start_indices)):
        start_time = gps_data.iloc[start_indices[i-1]]['Time']
        end_time = gps_data.iloc[start_indices[i]]['Time']
        lap_times.append(end_time - start_time)
    return lap_times

lap_times_1 = calculate_lap_times(gps_data_1, start_indices_1)
lap_times_2 = calculate_lap_times(gps_data_2, start_indices_2)

# Muudame loendid võrdse pikkusega
max_length = max(len(lap_times_1), len(lap_times_2))
lap_times_1.extend([None] * (max_length - len(lap_times_1)))
lap_times_2.extend([None] * (max_length - len(lap_times_2)))

# Koosta võrdlustabel
comparison_table = pd.DataFrame({
    'Lap Number (File 1)': list(range(1, len(lap_times_1) + 1)),
    'Lap Time (File 1)': lap_times_1,
    'Lap Number (File 2)': list(range(1, len(lap_times_2) + 1)),
    'Lap Time (File 2)': lap_times_2
})

print("Võrdlustabel:")
print(comparison_table)

# Kasutaja poolt määratud ringid
lap1 = int(input("Sisesta esimese faili ringi number: "))  # Kasutaja sisend
lap2 = int(input("Sisesta teise faili ringi number: "))  # Kasutaja sisend

# Ekstraheeri ringide andmed
lap_1_data = gps_data_1[gps_data_1['Lap'] == lap1].copy()
lap_2_data = gps_data_2[gps_data_2['Lap'] == lap2].copy()

# Muuda ringi ajad algama 0-st
lap_1_data['Time'] = lap_1_data['Time'] - lap_1_data['Time'].iloc[0]
lap_2_data['Time'] = lap_2_data['Time'] - lap_2_data['Time'].iloc[0]

# Valmista andmed plottimiseks
dataLap1 = np.array([lap_1_data['Time'], lap_1_data['GPS Speed'], lap_1_data['GPS Longitude'], lap_1_data['GPS Latitude']])
dataLap2 = np.array([lap_2_data['Time'], lap_2_data['GPS Speed'], lap_2_data['GPS Longitude'], lap_2_data['GPS Latitude']])

# Loo joonis plottimiseks
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_alpha(0)  # Eemalda figuuri taust
ax.patch.set_alpha(0)  # Eemalda telgede taust

line1, = ax.plot([], [], 'b-', label=f'Lap {lap1}')
line2, = ax.plot([], [], 'r-', label=f'Lap {lap2}')
point1, = ax.plot([], [], 'bo')
point2, = ax.plot([], [], 'ro')

ax.set_xlim(min(gps_data_1['GPS Longitude'].min(), gps_data_2['GPS Longitude'].min()), max(gps_data_1['GPS Longitude'].max(), gps_data_2['GPS Longitude'].max()))
ax.set_ylim(min(gps_data_1['GPS Latitude'].min(), gps_data_2['GPS Latitude'].min()), max(gps_data_1['GPS Latitude'].max(), gps_data_2['GPS Latitude'].max()))
ax.axis('off')  # Eemalda teljestik
plt.title(f'Comparison of Lap {lap1} and Lap {lap2} Trajectories')
plt.legend()

# Lisa telemeetria tekst
text = ax.text(0.95, 0.05, '', transform=ax.transAxes, fontsize=12,
               verticalalignment='bottom', horizontalalignment='right', bbox=dict(facecolor='white', alpha=0.5))

# Funktsioon, et uuendada animatsiooni kaadrit
def update(num):
    if num < len(dataLap1[0]):
        line1.set_data(dataLap1[2, :num], dataLap1[3, :num])
        point1.set_data([dataLap1[2, num]], [dataLap1[3, num]])
        time_elapsed_1 = dataLap1[0, num]
        speed_1 = dataLap1[1, num]
    else:
        line1.set_data(dataLap1[2, :], dataLap1[3, :])
        point1.set_data([dataLap1[2, -1]], [dataLap1[3, -1]])
        time_elapsed_1 = dataLap1[0, -1]
        speed_1 = dataLap1[1, -1]
    
    if num < len(dataLap2[0]):
        line2.set_data(dataLap2[2, :num], dataLap2[3, :num])
        point2.set_data([dataLap2[2, num]], [dataLap2[3, num]])
        time_elapsed_2 = dataLap2[0, num]
        speed_2 = dataLap2[1, num]
    else:
        line2.set_data(dataLap2[2, :], dataLap2[3, :])
        point2.set_data([dataLap2[2, -1]], [dataLap2[3, -1]])
        time_elapsed_2 = dataLap2[0, -1]
        speed_2 = dataLap2[1, -1]

    # Uuenda telgede piire, et suurendada vaadet ja liikuda koos punktiga
    zoom_factor = 6
    ax.set_xlim(dataLap1[2, num % len(dataLap1[0])] - 0.001 / zoom_factor, dataLap1[2, num % len(dataLap1[0])] + 0.001 / zoom_factor)
    ax.set_ylim(dataLap1[3, num % len(dataLap1[0])] - 0.001 / zoom_factor, dataLap1[3, num % len(dataLap1[0])] + 0.001 / zoom_factor)
    # Uuenda telemeetria teksti
    text.set_text(f'Lap {lap1} - Time: {time_elapsed_1:.2f} s, Speed: {speed_1:.2f} km/h\n'
                  f'Lap {lap2} - Time: {time_elapsed_2:.2f} s, Speed: {speed_2:.2f} km/h')
    
    # Lisa kiiruse sildid punktide juurde
    point1_speed.set_text(f'{speed_1:.2f} km/h')
    point1_speed.set_position((dataLap1[2, num % len(dataLap1[0])], dataLap1[3, num % len(dataLap1[0])]))
    
    point2_speed.set_text(f'{speed_2:.2f} km/h')
    point2_speed.set_position((dataLap2[2, num % len(dataLap2[0])], dataLap2[3, num % len(dataLap2[0])]))

    return line1, line2, point1, point2, text, point1_speed, point2_speed

# Loome kiiruse sildid punktide juurde
point1_speed = ax.text(0, 0, '', fontsize=10, color='blue', ha='right')
point2_speed = ax.text(0, 0, '', fontsize=10, color='red', ha='left')


# Loo animatsioon
max_frames = max(len(dataLap1[0]), len(dataLap2[0]))
ani = animation.FuncAnimation(fig, update, frames=max_frames, blit=True, interval=50)

# Salvesta animatsioon failina
ani.save('laps_comparison.mp4', writer='ffmpeg')
plt.show()
