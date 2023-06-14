from pynvml import *
import asyncio
import psutil
from rich import box
from rich import bar
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
from collections import defaultdict


def generate_table() -> Table:
    global gpus, ngpus
    
    outer_table = Table.grid()
    ui = outer_table
    
    cuda = nvmlSystemGetCudaDriverVersion()
    outer_table.add_row(
        Panel.fit(f"[bold]Driver Version: {nvmlSystemGetDriverVersion()}  CUDA Version: {cuda//1000}.{cuda%1000//10}", title="", border_style="magenta", padding=(0,2), title_align='left'),
    )
    for gpu_name in gpus:
        table = Table(show_header=False, header_style="bold magenta", padding=(0,1), show_edge=False)
        table.box = box.MINIMAL
        # table.add_column("GPU", style="cyan", justify="center", no_wrap=True)
        table.add_column("Util", style="green", justify="center", max_width=20)
        table.add_column("Mem", style="yellow", justify="center", max_width=30)
        table.add_column("Power", style="yellow", justify="center")
        table.add_column("Temp", style="blue", justify="center")
        table.add_column("Energy Consumption", style="red", justify="center")
        # table.add_column("GPU Clocks", style="magenta", justify="center")
        # table.add_column("Memory Clocks", style="magenta", justify="center")
        for gpu in gpus[gpu_name]:
            table.add_row(
                # f"[{gpu.get_id()}]",
                gpu.get_progress_utl(),
                gpu.get_progress_mem(),
                gpu.get_power(),
                gpu.get_temperture(),
                gpu.get_energy(),
            )
        outer_table.add_row(Panel.fit(table, title=gpu_name, border_style="magenta", padding=(0,0), title_align='left'))

    
    
    
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
    gpus = defaultdict(list)
    for idx in range(ngpus):
        handle = nvmlDeviceGetHandleByIndex(idx)
        name = nvmlDeviceGetName(handle)
        memory = nvmlDeviceGetMemoryInfo(handle)
        gpu_clocks_max = nvmlDeviceGetMaxClockInfo(handle, NVML_CLOCK_GRAPHICS)
        mem_clocks_max = nvmlDeviceGetMaxClockInfo(handle, NVML_CLOCK_MEM)
        gpus[name].append(GPU(
            idx,
            memory.total,
            gpu_clocks_max,
            mem_clocks_max
        ))

        gpus["NVIDIA RTX-3090"].append(GPU(
            idx,
            memory.total,
            gpu_clocks_max,
            mem_clocks_max
        ))

async def fetch_gpu_info():
    global gpus, ngpus
    while True:
        for gpu_name in gpus:
            for gpu in gpus[gpu_name]:
                handle = nvmlDeviceGetHandleByIndex(gpu.get_id())
                utilization = nvmlDeviceGetUtilizationRates(handle)
                power_usage = nvmlDeviceGetPowerUsage(handle) / 1000.0  # in watts
                temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
                energy_consumption = nvmlDeviceGetTotalEnergyConsumption(handle) / 1000.0 / 1000.0  # in kJoule
                gpu_clocks = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_GRAPHICS)
                mem_clocks = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_MEM)
                gpu_memory = nvmlDeviceGetMemoryInfo(handle)

                gpu.set_mem_used(gpu_memory.used)
                gpu.set_gpu_temperture(temperature)
                gpu.set_power(power_usage)
                gpu.set_utl(utilization.gpu)
                gpu.set_clocks(gpu_clocks, mem_clocks)
                gpu.set_energy(energy_consumption)        
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


