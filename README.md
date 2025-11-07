# Strength Level to markdown

### Introduction

This script allows you to convert a Strength Level CSV export to markdown files, one for each date. These markdown files can subsequently be imported into a note taking app, for instance.

### Requirements

- Python 3.8 or higher

### Installation

1. Clone this repository into a directory of your choice

```
cd /path/to/directory
git clone https://git.nelisss.net/niels/strengthleveltomd.git
```

1. Run install.sh to create a virtual environment with the required python packages installed

```
chmod +x install.sh
./install.sh
```

### Usage

**Download Strength Level CSV**

- Strength Level CSV: from https://my.strengthlevel.com/[username]/workouts, scroll to the bottom of the page and click Export CSV.

**Run the python script**

1. Activate the virtual environment

```
source venv/bin/activate
```

1. Run the python script

```
python strengthleveltomd.py [options]
```

The following options are recognized:

| Option           | Description                                                                 | Possible values                                                          |
|------------------|-----------------------------------------------------------------------------|--------------------------------------------------------------------------|
| \-h --help        | Print help.                                                                 | \-                                                                        |
| \-f --file        | Path to Strength Level CSV file. Default: interactive file picker.          | Valid path to CSV file or "interactive" to be prompted with file picker. |
| \-d --directory   | Output directory to save .md files to. Default: <working directory>/output. | Valid path to folder. Can create one folder, but not recursively.        |
| \-o --frontmatter | Type of frontmatter to add to .md files. Default: "none".                   | Currently only supports "joplin" or "none".                              |
| \-m --metric      | Whether to kg (true) or lb (false). Default: true.                          | true/t or false/f                                                        |
