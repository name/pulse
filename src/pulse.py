import psutil
import time
import os
import argparse
from collections import defaultdict
import csv
from datetime import datetime

def get_disk_io():
    return psutil.disk_io_counters(perdisk=True)

def calculate_iops(old, new, interval):
    read_iops = (new.read_count - old.read_count) / interval
    write_iops = (new.write_count - old.write_count) / interval
    return read_iops, write_iops

def get_top_io_processes(n=5):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'io_counters']):
        try:
            io_counters = proc.io_counters()
            io_total = io_counters.read_bytes + io_counters.write_bytes
            processes.append((proc.pid, proc.name(), io_total, io_counters.read_bytes, io_counters.write_bytes))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return sorted(processes, key=lambda x: x[2], reverse=True)[:n]

def get_top_io_files(n=5):
    file_io = defaultdict(lambda: {'read_bytes': 0, 'write_bytes': 0})
    for proc in psutil.process_iter(['pid', 'name', 'io_counters']):
        try:
            io_counters = proc.io_counters()
            for file in proc.open_files():
                file_io[file.path]['read_bytes'] += io_counters.read_bytes
                file_io[file.path]['write_bytes'] += io_counters.write_bytes
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return sorted(file_io.items(), key=lambda x: x[1]['read_bytes'] + x[1]['write_bytes'], reverse=True)[:n]

def monitor_all_disk_iops(interval=1, top_n=5, file_update_multiplier=3, log_prefix='disk_io'):
    print("Monitoring IOPS for all disks. Press Ctrl+C to stop.")
    max_iops = {}
    file_update_counter = 0
    top_files = []
    
    iops_log_file = f"{log_prefix}_iops.csv"
    process_log_file = f"{log_prefix}_processes.csv"
    file_log_file = f"{log_prefix}_files.csv"
    
    with open(iops_log_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Time', 'Drive', 'Read IOPS', 'Write IOPS', 'Max Read IOPS', 'Max Write IOPS'])
    
    with open(process_log_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Time', 'PID', 'Process', 'Total I/O (MB)', 'Read I/O (MB)', 'Write I/O (MB)'])
    
    with open(file_log_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Time', 'File Path', 'Read I/O (MB)', 'Write I/O (MB)'])
    
    try:
        previous_io = get_disk_io()
        while True:
            time.sleep(interval)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            current_io = get_disk_io()
            
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("Disk IOPS:")
            print("{:<15} {:<15} {:<15} {:<15} {:<15}".format("Drive", "Read IOPS", "Write IOPS", "Max Read IOPS", "Max Write IOPS"))
            print("-" * 75)
            
            with open(iops_log_file, 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                
                for drive, counters in current_io.items():
                    if drive in previous_io:
                        read_iops, write_iops = calculate_iops(previous_io[drive], counters, interval)
                        if drive not in max_iops:
                            max_iops[drive] = {'read': read_iops, 'write': write_iops}
                        else:
                            max_iops[drive]['read'] = max(max_iops[drive]['read'], read_iops)
                            max_iops[drive]['write'] = max(max_iops[drive]['write'], write_iops)
                        print("{:<15} {:<15.2f} {:<15.2f} {:<15.2f} {:<15.2f}".format(
                            drive, read_iops, write_iops, max_iops[drive]['read'], max_iops[drive]['write']))
                        
                        csvwriter.writerow([current_time, drive, read_iops, write_iops, max_iops[drive]['read'], max_iops[drive]['write']])
            
            top_processes = get_top_io_processes(top_n)
            
            print(f"\nTop {top_n} I/O Processes:")
            print("{:<10} {:<20} {:<15} {:<15} {:<15}".format("PID", "Process", "Total I/O (MB)", "Read I/O (MB)", "Write I/O (MB)"))
            print("-" * 75)
            
            with open(process_log_file, 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                for pid, name, total, read, write in top_processes:
                    total_mb = total / (1024*1024)
                    read_mb = read / (1024*1024)
                    write_mb = write / (1024*1024)
                    print("{:<10} {:<20} {:<15.2f} {:<15.2f} {:<15.2f}".format(
                        pid, name[:19], total_mb, read_mb, write_mb))
                    csvwriter.writerow([current_time, pid, name, total_mb, read_mb, write_mb])
            
            file_update_counter += 1
            if file_update_counter >= file_update_multiplier:
                top_files = get_top_io_files(top_n)
                file_update_counter = 0
            
            print(f"\nTop {top_n} I/O Files (updated every {file_update_multiplier} cycles):")
            print("{:<50} {:<15} {:<15}".format("File Path", "Read I/O (MB)", "Write I/O (MB)"))
            print("-" * 80)
            
            with open(file_log_file, 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                for file_path, io_data in top_files:
                    read_mb = io_data['read_bytes'] / (1024*1024)
                    write_mb = io_data['write_bytes'] / (1024*1024)
                    print("{:<50} {:<15.2f} {:<15.2f}".format(
                        file_path[:49], read_mb, write_mb))
                    csvwriter.writerow([current_time, file_path, read_mb, write_mb])
            
            previous_io = current_io
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor disk IOPS and top I/O processes")
    parser.add_argument("-n", "--num-processes", type=int, default=5, help="Number of top processes to display (default: 5)")
    parser.add_argument("-t", "--refresh-time", type=float, default=1.0, help="Refresh time in seconds (default: 1.0)")
    parser.add_argument("-f", "--file-update-multiplier", type=int, default=3, help="Multiplier for file info update interval (default: 3)")
    parser.add_argument("-l", "--log-prefix", type=str, default="disk_io", help="Prefix for log files (default: disk_io)")
    args = parser.parse_args()

    monitor_all_disk_iops(interval=args.refresh_time, top_n=args.num_processes, file_update_multiplier=args.file_update_multiplier, log_prefix=args.log_prefix)
