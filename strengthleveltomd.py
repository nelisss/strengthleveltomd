import tkinter as tk
from tkinter import filedialog
import getopt
import sys
import os
import pandas as pd
from tqdm import tqdm

### Get command-line arguments
args = sys.argv[1:]
options = "hf:d:o:m:"
long_options = ["help", "file=", "directory=", "frontmatter=", "metric="]

sl_csv_path = "interactive"
output_dir = os.getcwd()
frontmatter = "none"
metric = True

try:
    arguments, values = getopt.getopt(args, options, long_options)
    for arg, val in arguments:
        if arg in ("-h", "--help"):
            help_string = \
"""Usage: strengthleveltomd.py [-h] [-f <file>] [-d <output directory>] [-o <frontmatter>] [-m <true/false>]
Options:
    -h --help           : Print this help and exit.
    -f --file           : Path to Strength Level CSV file or "interactive". Default: interactive.
    -d --directory      : Output directory to save .md files to. Default: working directory.
    -o --frontmatter    : Type of frontmatter to add to .md files. Default: none. Currently only supports "joplin".
    -m --metric         : Whether to use kg (true) or lb (false). Default: true."""
            print(help_string)
            sys.exit()

        if arg in ("-f", "--file"):
            sl_csv_path = val
            if not os.path.exists(sl_csv_path):
                raise FileExistsError("\nProvided Strength Level CSV file path does not exist.")

        if arg in ("-d", "--directory"):
            output_dir = val
            if not os.path.exists(output_dir):
                try:
                    os.mkdir(output_dir)
                except Exception as e:
                    raise FileExistsError("\nProvided output directory does not exist and could not be created.") from e
            
        if arg in ("-o", "--frontmatter"):
            frontmatter = val
            if frontmatter not in ["none", "joplin"]:
                raise ValueError("\nProvided frontmatter is not supported. Possible values: none, joplin.")

        if arg in ("-m", "--metric"):
            metric = val
            if metric.lower() == "t" or metric.lower() == "true":
                metric = True
            elif metric.lower() == "f" or metric.lower() == "false":
                metric = False
            else:
                raise ValueError("\nInvalid value for argument metric. Should be true/t or false/f.")

except getopt.error as err:
    print(str(err))

print(" ")
print(f"Running strengthleveltomd with the following parameters:\n   Input file: {sl_csv_path}\n   Output directory: {output_dir}\n   Frontmatter: {frontmatter}\n   Metric: {metric}\n")

### Import Strength Level CSV
if sl_csv_path == "interactive":
    root = tk.Tk()
    root.withdraw()
    root.call("wm", "attributes", ".", "-topmost", True)
    sl_csv_path = filedialog.askopenfilename(
        title="Select Strength Level activities CSV", initialdir=os.getcwd()
    )
    print("Selected file:")
    print(sl_csv_path, "\n")

if metric:
    cols = ["Date Lifted", "Exercise", "Weight (kg)", "Reps", "Bodyweight (kg)", "Percentile (%)"]
    dtypes = {"Exercise": "str", "Weight (kg)": "float", "Reps": "Int64", "Bodyweight (kg)": "float", "Percentile (%)": "float"}
else:
    cols = ["Date Lifted", "Exercise", "Weight (lb)", "Reps", "Bodyweight (lb)", "Percentile (%)"]
    dtypes = {"Exercise": "str", "Weight (lb)": "float", "Reps": "Int64", "Bodyweight (lb)": "float", "Percentile (%)": "float"}

activities = pd.read_csv(sl_csv_path, na_values="", decimal=".", 
    usecols=cols,
    dtype=dtypes)

### Preprocessing of DataFrame
activities["Date Lifted"] = pd.to_datetime(activities["Date Lifted"])

### Convert each row to markdown file
unique_dates = activities["Date Lifted"].unique()
with tqdm(total=len(unique_dates), desc="Converting to markdown") as pbar:
    for date_ind, date in enumerate(unique_dates):
        df_date = activities.loc[activities["Date Lifted"] == date, :].reset_index()

        # Add frontmatter if specified
        if frontmatter == "joplin": 
            frontmatter_string = \
f"""---
title: \"Strength Level Workout {date.strftime("%Y-%m-%d")}\"
created: {str(date.isoformat()).replace("T", " ").replace("+00:00", "") + "Z"}
---

"""
        else:
            frontmatter_string = ""

        # Add workout summary
        total_sets = len(df_date.index)
        total_reps = df_date["Reps"].sum()
        total_volume = (df_date[("Weight (kg)" if metric else "Weight (lb)")] * df_date["Reps"]).sum()
        unique_exercises = df_date["Exercise"].unique()

        content_string = \
f"""Strength Level Workout on {date.strftime("%A %B %-d %Y")}
{len(unique_exercises)} exercises, {total_sets} total sets, {total_reps} total reps, {total_volume} {"kg" if metric else "lb"} total volume, {df_date.loc[0, ("Bodyweight (kg)" if metric else "Bodyweight (lb)")]} {"kg" if metric else "lb"} bodyweight.
"""
        exercise_ind = 0
        for exercise in unique_exercises:
            unique_weights = df_date.loc[df_date["Exercise"] == exercise, ("Weight (kg)" if metric else "Weight (lb)")].unique()

            content_string = content_string + f"\n{exercise}:"
            exercise_ind = exercise_ind + 1

            if not pd.isna(unique_weights[0]):
                weight_ind = 0
                for weight in unique_weights:
                    unique_reps = df_date.loc[(df_date["Exercise"] == exercise) & (df_date[("Weight (kg)" if metric else "Weight lb")] == weight), "Reps"].unique()

                    content_string = content_string + f"\n   {weight} {"kg" if metric else "lb"}: "
                    weight_ind = weight_ind + 1

                    rep_ind = 0
                    for reps in unique_reps:
                        n_sets_at_rep = len(df_date.loc[(df_date["Exercise"] == exercise) & (df_date[("Weight (kg)" if metric else "Weight lb")] == weight) & (df_date["Reps"] == reps), :].index)
                        content_string = content_string + f"{", " if rep_ind > 0 else ""}{n_sets_at_rep} x {reps}"
                        rep_ind = rep_ind + 1
            else:
                unique_reps = df_date.loc[df_date["Exercise"] == exercise, "Reps"].unique()
                if not pd.isna(unique_reps[0]):
                    rep_ind = 0
                    for reps in unique_reps:
                        n_sets_at_rep = len(df_date.loc[(df_date["Exercise"] == exercise) & (df_date["Reps"] == reps), :].index)
                        content_string = content_string + f"{", " if rep_ind > 0 else " "}{n_sets_at_rep} x {reps}"
                        rep_ind = rep_ind + 1
                else:
                    content_string = content_string + " -"

        file_name = f"Strength_Level_Workout_{df_date.loc[0, "Date Lifted"].strftime("%Y-%m-%d")}"

        with open(f"{output_dir}{"/" if output_dir[-1] != "/" else ""}{file_name}.md", "w", encoding="utf-8") as md_file:
            md_file.write(frontmatter_string + content_string)

        pbar.update(1)
