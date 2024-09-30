# Pulse

This tool monitors disk IOPS (Input/Output Operations Per Second) and displays the top I/O-consuming processes and files on your system.

## Usage

Run the script with Python:

```
python pulse.py [options]
```

Or use the compiled executable:

```
pulse.exe [options]
```

### Options

-   `-n`, `--num-processes`: Number of top processes and files to display (default: 5)
-   `-t`, `--refresh-time`: Refresh time in seconds (default: 1.0)
-   `-f`, `--file-update-multiplier`: Multiplier for file info update interval (default: 3)
-   `-l`, `--log-prefix`: Prefix for log files (default: disk_io)

Example:

```
pulse.exe -n 10 -t 2 -f 5 -l my_log
```

This will display the top 10 I/O processes and files, refresh every 2 seconds, update file information every 10 seconds (2 \* 5), and create log files with the prefix 'my_log'.

## Building to Executable

To compile the script into a standalone executable:

1. Install PyInstaller:
   `pip install pyinstaller`

2. Navigate to the directory containing `pulse.py`

3. Run PyInstaller:
   `py -m PyInstaller --onefile pulse.py`

4. Find the executable in the `dist` folder

## Features

-   Monitors IOPS for all physical drives
-   Displays top I/O-consuming processes
-   Shows top I/O-intensive files (updated less frequently to improve performance)
-   Real-time updates with customizable refresh rates
-   Logs IOPS, process, and file I/O data to separate CSV files for further analysis

## Requirements

-   Python 3.6+
-   psutil library

To install psutil:

```
pip install psutil
```

## Note

Running the executable or script may require administrator privileges to access all system information. The file I/O information is gathered less frequently than process information to reduce system load.

## Log File Formats

The script creates three separate log files:

1. IOPS log file ({prefix}\_iops.csv):
   Time,Drive,Read IOPS,Write IOPS,Max Read IOPS,Max Write IOPS

2. Process log file ({prefix}\_processes.csv):
   Time,PID,Process,Total I/O (MB),Read I/O (MB),Write I/O (MB)

3. File log file ({prefix}\_files.csv):
   Time,File Path,Read I/O (MB),Write I/O (MB)

These CSV formats allow for easy import into spreadsheet software for further analysis.
