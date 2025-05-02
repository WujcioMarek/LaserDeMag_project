"""
Data saving and reading support.
"""
import json
import csv

def save_to_csv(filename, t, Te, Tl, Ts):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time', 'Te', 'Tl', 'Ts'])
        for i in range(len(t)):
            writer.writerow([t[i], Te[i], Tl[i], Ts[i]])

def load_config(file):
    with open(file) as f:
        return json.load(f)