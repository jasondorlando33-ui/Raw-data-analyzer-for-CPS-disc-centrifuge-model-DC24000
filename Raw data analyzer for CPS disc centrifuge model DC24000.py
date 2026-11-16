#!/usr/bin/env python
# coding: utf-8

# In[3]:


print("starting up")
from pathlib import Path
print("pathlib, library for handling filesystem paths, loaded")
import pandas as pd
print("pandas, Python Data Analysis Library, loaded")
import numpy as np
print("numpy, library for numerical computing, loaded")


# In[31]:


while True:
    print("\n" + "="*90)
    title = "📊📈 DISC CENTRIFUGE RAW DATA ANALYZER 📈📊"
    print(f"{title:^90}")
    print("="*90 + "\n")
    print('[1] Run data analyzer program')
    print('[2] close the program')
    print("-"*90)
    program_status = input('User input: ')
    if program_status == '2':
        print("\nGood luck with data analysis")
        print("     -Jason D. Orlando Ph.D.")
        break
    if program_status not in ['1', '2']:
        print("Not a valid entry. Returning to main menu")
        continue

    stats = []
    graph_data = {}

    folder = Path.cwd()

    for file in folder.glob("*.dat"):
        sample = file.stem
        print(f"\nloaded sample: {sample}")
        df = pd.read_csv(file, header=21)
        df = df.T.reset_index().T.reset_index(drop=True)
        df.columns= ["diameter","signal"]
        df['signal'] = df['signal'].astype('float64')
        df['diameter'] = df['diameter'].astype('float64')

        print(f"-----extracting raw data for graphs")
        graph_data[f"{sample} (diameter)"] = df["diameter"]
        graph_data[f"{sample} (signal*diameter)"] = df['signal']

        print(f"-----calculating descriptive statistics")
        df['signal'] = df["signal"].clip(lower=0)
        clipped_signal = df["signal"].clip(lower=0)
        tmp = pd.DataFrame({
            "diameter": df["diameter"],
            "signal": clipped_signal
        }).sort_values("diameter").reset_index(drop=True)

        # Area under the curve
        delta_d = np.diff(tmp["diameter"])
        area = tmp["signal"].iloc[:-1].values * delta_d
        area = area / area.sum()

        diameter = tmp["diameter"].iloc[:-1].values

        # relative int at 0.1 micron
        idx_100nm = (tmp["diameter"] - 0.1).abs().idxmin()
        signal_100nm = tmp.loc[idx_100nm, "signal"]
        rel_signal_100nm = signal_100nm / tmp["signal"].max() * 100

        main_peak = float((tmp.loc[tmp["signal"] == tmp['signal'].max(), 'diameter']).iloc[0])

        mean_wt = np.sum(area * diameter)
        cumulative_sum = np.cumsum(area)

        d50 = np.interp(0.5, cumulative_sum, diameter)
        d10 = np.interp(0.10, cumulative_sum, diameter)
        d25 = np.interp(0.25, cumulative_sum, diameter)
        d75 = np.interp(0.75, cumulative_sum, diameter)
        d90 = np.interp(0.90, cumulative_sum, diameter)
        d95 = np.interp(0.95, cumulative_sum, diameter)

        diameter = tmp["diameter"].iloc[:-1].values
        weight_fraction = area
        number_fraction = weight_fraction / diameter**3
        number_fraction /= number_fraction.sum()
        mean_number = np.sum(number_fraction * diameter)
        PDI = mean_wt / mean_number


        row = {
            "sample": sample,
            "mode of main band (nm)": main_peak *1000,
            "median (nm)":d50 *1000,
            "mean wt (nm)": mean_wt *1000,            
            "d10 (nm)": d10 *1000,
            "d25 (nm)": d25 *1000,
            "d75 (nm)": d75 *1000,
            "d90 (nm)": d90 *1000,
            "d95 (nm)": d95 *1000,
            "polydispersity": PDI,
            "relative int at 0.1 micron": rel_signal_100nm,
        }
        stats.append(row)

    print("\nCompiling raw data and building stats table")
    df_graph_data = pd.DataFrame(graph_data)
    df_stats = pd.DataFrame(stats)
    output_path = folder / "disc centrfuge raw data and stats.xlsx"

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df_stats.to_excel(writer, sheet_name='stats')
            df_graph_data.to_excel(writer, sheet_name='graph data')
    print(f"\nfile 'disc centrfuge raw data and stats.xlsx' has been saved to: {output_path}")


# In[28]:


main_peak = float((tmp.loc[tmp["signal"] == tmp['signal'].max(), 'diameter']).iloc[0])
main_peak


# In[ ]:




