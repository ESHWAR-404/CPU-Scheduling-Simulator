import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import os

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0

class ProcessScheduler:
    def __init__(self):
        self.processes = []
        self.gantt_chart = []
    
    def add_process(self, pid, arrival_time, burst_time, priority=0):
        self.processes.append(Process(pid, arrival_time, burst_time, priority))
        
    def reset_processes(self):
        for process in self.processes:
            process.completion_time = 0
            process.turnaround_time = 0
            process.waiting_time = 0
            process.remaining_time = process.burst_time
            
    def calculate_times(self):
        for process in self.processes:
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            
    def plot_gantt_chart(self):
        fig, ax = plt.subplots(figsize=(12, 3))
        
        for i, (pid, start, end) in enumerate(self.gantt_chart):
            ax.barh(0, end - start, left=start, height=0.3, 
                   align='center', color=f'C{pid % 10}', 
                   edgecolor='black')
            
            ax.text((start + end)/2, 0, f'P{pid}',
                   ha='center', va='center')
            
        ax.set_ylim(-0.5, 0.5)
        ax.set_xlabel('Time')
        ax.set_title('Gantt Chart')
        ax.grid(True)
        
        plt.show()
        
    def print_results(self):
        print("\nProcess Execution Details:")
        print("PID\tAT\tBT\tCT\tTAT\tWT")
        
        total_tat = total_wt = 0
        for p in self.processes:
            print(f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\t{p.completion_time}\t"
                  f"{p.turnaround_time}\t{p.waiting_time}")
            total_tat += p.turnaround_time
            total_wt += p.waiting_time
            
        n = len(self.processes)
        print(f"\nAverage Turnaround Time: {total_tat/n:.2f}")
        print(f"Average Waiting Time: {total_wt/n:.2f}")

    def fcfs(self):
        self.processes.sort(key=lambda x: (x.arrival_time, x.pid))
        current_time = 0
        self.gantt_chart = []
        
        for process in self.processes:
            if current_time < process.arrival_time:
                current_time = process.arrival_time
                
            self.gantt_chart.append((process.pid, current_time, current_time + process.burst_time))
            current_time += process.burst_time
            process.completion_time = current_time
            
        self.calculate_times()
        
    def sjf_nonpreemptive(self):
        remaining_processes = self.processes.copy()
        current_time = 0
        self.gantt_chart = []
        
        while remaining_processes:
            available_processes = [p for p in remaining_processes 
                                if p.arrival_time <= current_time]
            
            if not available_processes:
                current_time = min(p.arrival_time for p in remaining_processes)
                continue
                
            next_process = min(available_processes, 
                             key=lambda x: (x.burst_time, x.arrival_time))
            
            self.gantt_chart.append((next_process.pid, current_time, 
                                   current_time + next_process.burst_time))
            
            current_time += next_process.burst_time
            next_process.completion_time = current_time
            remaining_processes.remove(next_process)
            
        self.calculate_times()
        
    def sjf_preemptive(self):
        remaining_processes = self.processes.copy()
        current_time = 0
        self.gantt_chart = []
        
        for p in self.processes:
            p.remaining_time = p.burst_time
            
        prev_process = None
        start_time = 0
        
        while remaining_processes:
            available_processes = [p for p in remaining_processes 
                                if p.arrival_time <= current_time]
            
            if not available_processes:
                current_time = min(p.arrival_time for p in remaining_processes)
                continue
                
            next_process = min(available_processes, 
                             key=lambda x: (x.remaining_time, x.arrival_time))
            
            if prev_process != next_process:
                if prev_process is not None:
                    self.gantt_chart.append((prev_process.pid, start_time, current_time))
                start_time = current_time
                prev_process = next_process
                
            current_time += 1
            next_process.remaining_time -= 1
            
            if next_process.remaining_time == 0:
                next_process.completion_time = current_time
                remaining_processes.remove(next_process)
                self.gantt_chart.append((next_process.pid, start_time, current_time))
                prev_process = None
                
        self.calculate_times()
        
    def round_robin(self, time_quantum):
        remaining_processes = deque(sorted(self.processes, key=lambda x: x.arrival_time))
        current_time = 0
        self.gantt_chart = []
        
        for p in self.processes:
            p.remaining_time = p.burst_time
            
        ready_queue = deque()
        
        while remaining_processes or ready_queue:
            while (remaining_processes and 
                   remaining_processes[0].arrival_time <= current_time):
                ready_queue.append(remaining_processes.popleft())
                
            if not ready_queue:
                current_time = remaining_processes[0].arrival_time
                continue
                
            process = ready_queue.popleft()
            
            execution_time = min(time_quantum, process.remaining_time)
            self.gantt_chart.append((process.pid, current_time, 
                                   current_time + execution_time))
            
            current_time += execution_time
            process.remaining_time -= execution_time
            
            while (remaining_processes and 
                   remaining_processes[0].arrival_time <= current_time):
                ready_queue.append(remaining_processes.popleft())
                
            if process.remaining_time > 0:
                ready_queue.append(process)
            else:
                process.completion_time = current_time
                
        self.calculate_times()
        
    def priority_nonpreemptive(self):
        remaining_processes = self.processes.copy()
        current_time = 0
        self.gantt_chart = []
        
        while remaining_processes:
            available_processes = [p for p in remaining_processes 
                                if p.arrival_time <= current_time]
            
            if not available_processes:
                current_time = min(p.arrival_time for p in remaining_processes)
                continue
                
            next_process = min(available_processes, 
                             key=lambda x: (x.priority, x.arrival_time))
            
            self.gantt_chart.append((next_process.pid, current_time, 
                                   current_time + next_process.burst_time))
            
            current_time += next_process.burst_time
            next_process.completion_time = current_time
            remaining_processes.remove(next_process)
            
        self.calculate_times()
        
    def priority_preemptive(self):
        remaining_processes = self.processes.copy()
        current_time = 0
        self.gantt_chart = []
        
        for p in self.processes:
            p.remaining_time = p.burst_time
            
        prev_process = None
        start_time = 0
        
        while remaining_processes:
            available_processes = [p for p in remaining_processes 
                                if p.arrival_time <= current_time]
            
            if not available_processes:
                current_time = min(p.arrival_time for p in remaining_processes)
                continue
                
            next_process = min(available_processes, 
                             key=lambda x: (x.priority, x.arrival_time))
            
            if prev_process != next_process:
                if prev_process is not None:
                    self.gantt_chart.append((prev_process.pid, start_time, current_time))
                start_time = current_time
                prev_process = next_process
                
            current_time += 1
            next_process.remaining_time -= 1
            
            if next_process.remaining_time == 0:
                next_process.completion_time = current_time
                remaining_processes.remove(next_process)
                self.gantt_chart.append((next_process.pid, start_time, current_time))
                prev_process = None
                
        self.calculate_times()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    scheduler = ProcessScheduler()
    
    while True:
        clear_screen()
        print("\n=== Process Scheduling Simulator ===")
        print("\nMain Menu:")
        print("1. Add Process")
        print("2. View All Processes")
        print("3. Run FCFS Scheduling")
        print("4. Run SJF (Non-preemptive) Scheduling")
        print("5. Run SJF (Preemptive) Scheduling")
        print("6. Run Round Robin Scheduling")
        print("7. Run Priority (Non-preemptive) Scheduling")
        print("8. Run Priority (Preemptive) Scheduling")
        print("9. Clear All Processes")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-9): ")
        
        if choice == '1':
            try:
                pid = len(scheduler.processes) + 1
                arrival_time = int(input("Enter arrival time: "))
                burst_time = int(input("Enter burst time: "))
                priority = int(input("Enter priority (lower number = higher priority): "))
                
                scheduler.add_process(pid, arrival_time, burst_time, priority)
                print("\nProcess added successfully!")
                input("\nPress Enter to continue...")
                
            except ValueError:
                print("\nPlease enter valid numeric values!")
                input("\nPress Enter to continue...")
                
        elif choice == '2':
            if not scheduler.processes:
                print("\nNo processes available!")
            else:
                print("\nCurrent Processes:")
                print("PID\tArrival Time\tBurst Time\tPriority")
                for p in scheduler.processes:
                    print(f"{p.pid}\t{p.arrival_time}\t\t{p.burst_time}\t\t{p.priority}")
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            if not scheduler.processes:
                print("\nNo processes available! Please add processes first.")
            else:
                scheduler.reset_processes()
                scheduler.fcfs()
                scheduler.print_results()
                scheduler.plot_gantt_chart()
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            if not scheduler.processes:
                print("\nNo processes available! Please add processes first.")
            else:
                scheduler.reset_processes()
                scheduler.sjf_nonpreemptive()
                scheduler.print_results()
                scheduler.plot_gantt_chart()
            input("\nPress Enter to continue...")
            
        elif choice == '5':
            if not scheduler.processes:
                print("\nNo processes available! Please add processes first.")
            else:
                scheduler.reset_processes()
                scheduler.sjf_preemptive()
                scheduler.print_results()
                scheduler.plot_gantt_chart()
            input("\nPress Enter to continue...")
            
        elif choice == '6':
            if not scheduler.processes:
                print("\nNo processes available! Please add processes first.")
            else:
                try:
                    time_quantum = int(input("Enter time quantum: "))
                    scheduler.reset_processes()
                    scheduler.round_robin(time_quantum)
                    scheduler.print_results()
                    scheduler.plot_gantt_chart()
                except ValueError:
                    print("\nPlease enter a valid time quantum!")
            input("\nPress Enter to continue...")
            
        elif choice == '7':
            if not scheduler.processes:
                print("\nNo processes available! Please add processes first.")
            else:
                scheduler.reset_processes()
                scheduler.priority_nonpreemptive()
                scheduler.print_results()
                scheduler.plot_gantt_chart()
            input("\nPress Enter to continue...")
            
        elif choice == '8':
            if not scheduler.processes:
                print("\nNo processes available! Please add processes first.")
            else:
                scheduler.reset_processes()
                scheduler.priority_preemptive()
                scheduler.print_results()
                scheduler.plot_gantt_chart()
            input("\nPress Enter to continue...")
            
        elif choice == '9':
            scheduler.processes.clear()
            print("\nAll processes cleared!")
            input("\nPress Enter to continue...")
            
        elif choice == '0':
            print("\nThank you for using the Process Scheduler!")
            break
            
        else:
            print("\nInvalid choice! Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
