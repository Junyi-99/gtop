from pynvml import *
import random

nvmlInit()
deviceCount = nvmlDeviceGetCount()

for i in range(deviceCount):
    handle = nvmlDeviceGetHandleByIndex(i)
    print(f"Device {i} : {nvmlDeviceGetName(handle)}")

    memory = nvmlDeviceGetMemoryInfo(handle)
    
    print(f"Device {i} : {round(memory.used / 1024/1024/1024, 1)}/{round(memory.total / 1024 / 1024 / 1024, 1)} GB, {round(memory.free / 1024**3)} GB free")
    print(f"Device {i} : {nvmlDeviceGetUtilizationRates(handle)}")
    print(f"Device {i} : Power Usage {nvmlDeviceGetPowerUsage(handle)/1000} W")
    print(f"Device {i} : Temp {nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)} °C")
    print(f"Device {i} : PCI {nvmlDeviceGetPciInfo(handle)}")
    print(f"Device {i} : Compute Process {nvmlDeviceGetComputeRunningProcesses(handle)}")
    print(f"Device {i} : Graphic Process {nvmlDeviceGetGraphicsRunningProcesses(handle)}")
    print(f"Device {i} : {nvmlDeviceGetProcessUtilization(handle, 0)}")
    print(f"Device {i} : Shutdown temp {nvmlDeviceGetTemperatureThreshold(handle, 0)}")
    print(f"Device {i} : Slowdown temp {nvmlDeviceGetTemperatureThreshold(handle, 1)}")
    print(f"Device {i} : Memory temp {nvmlDeviceGetTemperatureThreshold(handle, 2)} to slow down")
    print(f"Device {i} : Energy consumption {nvmlDeviceGetTotalEnergyConsumption(handle)/1000/1000} kJoule")
    print(f"Device {i} : PCI-E speed { nvmlDeviceGetPcieSpeed(handle)/1000 } Gbps")
    print(f"Device {i} : PCIE TX: {nvmlDeviceGetPcieThroughput(handle, NVML_PCIE_UTIL_TX_BYTES)/1024/1024} MB")
    print(f"Device {i} : PCIE RX: {nvmlDeviceGetPcieThroughput(handle, NVML_PCIE_UTIL_RX_BYTES)/1024/1024} MB")
    print(f"Device {i} : PCIE Link Width: {nvmlDeviceGetCurrPcieLinkWidth(handle)} %")
    print(f"Device {i} : PCIE Link Gen: {nvmlDeviceGetCurrPcieLinkGeneration(handle)} %")
    print(f"Device {i} : Gpu Cores: {nvmlDeviceGetNumGpuCores(handle)}")
    print(f"Device {i} : Gpu Clock: {nvmlDeviceGetClockInfo(handle, NVML_CLOCK_GRAPHICS)}/{nvmlDeviceGetMaxClockInfo(handle, NVML_CLOCK_GRAPHICS)} MHz")
    print(f"Device {i} : Memory Clock: {nvmlDeviceGetClockInfo(handle, NVML_CLOCK_MEM)}/{nvmlDeviceGetMaxClockInfo(handle, NVML_CLOCK_MEM)} MHz")
    
pid = 367537
nvmlSystemGetProcessName(pid)





"""

Demonstrates the use of multiple Progress instances in a single Live display.    

"""

from time import sleep

from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table


job_progress = Progress(
    "{task.description}",
    SpinnerColumn(),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
)

jobs = [None] * deviceCount
for i in range(deviceCount):
    jobs[i] = job_progress.add_task(f"[green]GPU {i}", total=100)

total = sum(task.total for task in job_progress.tasks)

overall_progress = Progress()
overall_task = overall_progress.add_task("All Jobs", total=int(total))

progress_table = Table.grid()
progress_table.add_row(
    Panel.fit(
        overall_progress, title="All GPUs Utilization", border_style="green", padding=(2, 2)
    ),
    Panel.fit(job_progress, title="[bold]GPUs", border_style="red", padding=(1, 2)),
)

with Live(progress_table, refresh_per_second=10):
    while not overall_progress.finished:

        for i in range(deviceCount):
            job_progress.update(jobs[i], completed=random.randint(0, 100))
            # job_progress.advance(jobs[i], random.randint(0, 100))
        sleep(0.1)
        # for job in job_progress.tasks:
        #     if not job.finished:
        #         job_progress.advance(job.id)
        #     job.update()
        # completed = sum(task.completed for task in job_progress.tasks)
        # overall_progress.update(overall_task, completed=completed)