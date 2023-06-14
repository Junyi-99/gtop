from pynvml import *
import asyncio
import psutil
from rich import box
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import print
import sys
import time
from rich.panel import Panel
from time import sleep
from gpu import GPU



def generate_table() -> Table:
    global gpus, ngpus
    
    table = Table(show_header=True, header_style="bold magenta")
    ui = Panel.fit(
        table, title="", border_style="magenta", padding=(0,0)
    )
    table.box = box.SIMPLE_HEAD
    table.add_column("GPU", style="cyan", justify="center", no_wrap=True)
    table.add_column("Util", style="green", justify="center", max_width=20)
    table.add_column("Mem", style="yellow", justify="center", max_width=30)
    table.add_column("Power", style="yellow", justify="center")
    table.add_column("Temp", style="blue", justify="center")
    # table.add_column("Energy Consumption", style="red", justify="center")
    # table.add_column("GPU Clocks", style="magenta", justify="center")
    # table.add_column("Memory Clocks", style="magenta", justify="center")
    
    
    table.add_section()

    global progress_gpu_utl, progress_gpu_mem, progress_gpu_mem_jobs, progress_gpu_utl_jobs

    for i in range(ngpus):
        table.add_row(
            gpus[i].get_id(),
            gpus[i].get_progress_utl(),
            gpus[i].get_progress_mem(),
            gpus[i].get_power(),
            gpus[i].get_temperture()
        )
    
    # for i in range(ngpus):
    #     gpu = nvmlDeviceGetHandleByIndex(i)
    #     gpu_name = nvmlDeviceGetName(gpu)
    #     utilization = nvmlDeviceGetUtilizationRates(gpu)
    #     power_usage = nvmlDeviceGetPowerUsage(gpu) / 1000.0  # in watts
    #     temperature = nvmlDeviceGetTemperature(gpu, NVML_TEMPERATURE_GPU)
    #     energy_consumption = nvmlDeviceGetTotalEnergyConsumption(gpu) / 1000.0 / 1000.0  # in kJoule
    #     gpu_clocks = nvmlDeviceGetClockInfo(gpu, NVML_CLOCK_GRAPHICS)
    #     gpu_clocks_max = nvmlDeviceGetMaxClockInfo(gpu, NVML_CLOCK_GRAPHICS)
    #     mem_clocks = nvmlDeviceGetClockInfo(gpu, NVML_CLOCK_MEM)
    #     mem_clocks_max = nvmlDeviceGetMaxClockInfo(gpu, NVML_CLOCK_MEM)
    #     gpu_memory = nvmlDeviceGetMemoryInfo(gpu)
        
    return ui

async def init_gpu_info():
    global gpus, ngpus

    # if nvml
    nvmlInit()
    ngpus = nvmlDeviceGetCount()
    gpus = [None] * ngpus
    for i in range(ngpus):
        handle = nvmlDeviceGetHandleByIndex(i)
        name = nvmlDeviceGetName(handle)
        memory = nvmlDeviceGetMemoryInfo(handle)
        gpu_clocks_max = nvmlDeviceGetMaxClockInfo(handle, NVML_CLOCK_GRAPHICS)
        mem_clocks_max = nvmlDeviceGetMaxClockInfo(handle, NVML_CLOCK_MEM)
        gpus[i] = GPU(
            str(i),
            memory.total,
            gpu_clocks_max,
            mem_clocks_max
        )

async def fetch_gpu_info():
    global gpus, ngpus
    while True:
        for i in range(ngpus):
            gpu = nvmlDeviceGetHandleByIndex(i)
        
            utilization = nvmlDeviceGetUtilizationRates(gpu)
            power_usage = nvmlDeviceGetPowerUsage(gpu) / 1000.0  # in watts
            temperature = nvmlDeviceGetTemperature(gpu, NVML_TEMPERATURE_GPU)
            energy_consumption = nvmlDeviceGetTotalEnergyConsumption(gpu) / 1000.0 / 1000.0  # in kJoule
            gpu_clocks = nvmlDeviceGetClockInfo(gpu, NVML_CLOCK_GRAPHICS)
            mem_clocks = nvmlDeviceGetClockInfo(gpu, NVML_CLOCK_MEM)
            gpu_memory = nvmlDeviceGetMemoryInfo(gpu)

            gpus[i].set_mem_used(gpu_memory.used)
            gpus[i].set_gpu_temperture(temperature)
            gpus[i].set_power(power_usage)
            gpus[i].set_utl(utilization.gpu)
            gpus[i].set_clocks(gpu_clocks, mem_clocks)
            gpus[i].set_energy(energy_consumption)
        await asyncio.sleep(0.5)

async def update_table():
    with Live(generate_table(), refresh_per_second=2) as live:
        while True:
            live.update(generate_table())
            await asyncio.sleep(0.5)

async def main():
    await init_gpu_info()
    await asyncio.gather(fetch_gpu_info(), update_table())


if __name__ == "__main__":
    console = Console()
    global gpus, ngpus

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        console.print_exception(show_locals=True)
    finally:
        nvmlShutdown()


