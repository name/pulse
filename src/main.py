import psutil
import time
import os
import argparse

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

def monitor_all_disk_iops(interval=1, top_n=5):
    print("Monitoring IOPS for all disks. Press Ctrl+C to stop.")
    max_iops = {}
    
    try:
        previous_io = get_disk_io()
        while True:
            time.sleep(interval)
            current_io = get_disk_io()
            
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("Disk IOPS:")
            print("{:<15} {:<15} {:<15} {:<15} {:<15}".format("Drive", "Read IOPS", "Write IOPS", "Max Read IOPS", "Max Write IOPS"))
            print("-" * 75)
            
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
            
            print(f"\nTop {top_n} I/O Processes:")
            print("{:<10} {:<20} {:<15} {:<15} {:<15}".format("PID", "Process", "Total I/O (MB)", "Read I/O (MB)", "Write I/O (MB)"))
            print("-" * 75)
            top_processes = get_top_io_processes(top_n)
            for pid, name, total, read, write in top_processes:
                print("{:<10} {:<20} {:<15.2f} {:<15.2f} {:<15.2f}".format(
                    pid, name[:19], total / (1024*1024), read / (1024*1024), write / (1024*1024)))
            
            previous_io = current_io
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor disk IOPS and top I/O processes")
    parser.add_argument("-n", "--num-processes", type=int, default=5, help="Number of top processes to display (default: 5)")
    parser.add_argument("-t", "--refresh-time", type=float, default=1.0, help="Refresh time in seconds (default: 1.0)")
    args = parser.parse_args()

    monitor_all_disk_iops(interval=args.refresh_time, top_n=args.num_processes)
