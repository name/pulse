# Disk IOPS Monitor

This tool monitors disk IOPS (Input/Output Operations Per Second) and displays the top I/O-consuming processes on your system.

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

-   `-n`, `--num-processes`: Number of top processes to display (default: 5)
-   `-t`, `--refresh-time`: Refresh time in seconds (default: 1.0)

Example:

```
pulse.exe -n 10 -t 2
```

This will display the top 10 I/O processes and refresh every 2 seconds.

## Building to Executable

To compile the script into a standalone executable:

1. Install PyInstaller:

```
pip install pyinstaller
```

2. Navigate to the directory containing `pulse.py`

3. Run PyInstaller:

```
py -m PyInstaller --onefile pulse.py
```

4. Find the executable in the `dist` folder

## Requirements

-   Python 3.6+
-   psutil library

To install psutil:

```
pip install psutil
```

## Note

Running the executable or script may require administrator privileges to access all system information.
