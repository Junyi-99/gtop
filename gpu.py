
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import bar

def bytes_to_human_readable(bytes: int) -> str:
    if bytes < 1024:
        return str(round(bytes,1)) + "B"
    elif bytes < 1024 ** 2:
        return str(round(bytes / 1024,1)) + "KiB"
    elif bytes < 1024 ** 3:
        return str(round(bytes / 1024 ** 2,1)) + "MiB"
    elif bytes < 1024 ** 4:
        return str(round(bytes / 1024 ** 3,1)) + "GiB"
    elif bytes < 1024 ** 5:
        return str(round(bytes / 1024 ** 4,1)) + "TiB"
    else:
        return str(round(bytes / 1024 ** 5,1)) + "PiB"

class GPU:
    def __init__(self, id, mem_total: int, gpu_clocks_max: int, mem_clocks_max) -> None:
        pass
        self.id = id
        self.utl = 0 # 0 ~ 100 integer
        self.mem_used = 0 # bytes
        self.mem_free = 0 # bytes

        self.power = 0 # in watts
        self.temperture = 0 # in celsius
        self.energy = 0 # in kJoule
        self.gpu_clocks = 0 # in MHz
        self.mem_clocks = 0 # in MHz
        
        self.mem_total = mem_total # bytes
        self.gpu_clocks_max = gpu_clocks_max # in MHz
        self.mem_clocks_max = mem_clocks_max # in MHz

        self.progress_utl = Progress(
            TextColumn("[dodger_blue3][{task.fields[gpuid]}] [bold blue]UTL"),
            SpinnerColumn(),
            BarColumn(finished_style = "red", ),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        self.progress_utl.add_task("GPU Utilization", total = 100)
        self.progress_utl.update(0, gpuid=self.id)

        self.progress_mem = Progress(
            TextColumn("[bold blue]MEM"),
            SpinnerColumn(),
            BarColumn(finished_style = "red", complete_style="spring_green4"),
            TextColumn("[progress.percentage]{task.fields[mem_used]:>8s}/{task.fields[mem_total]}"),
        )
        self.progress_mem.add_task("GPU Memory", total = self.mem_total)
        self.progress_mem.update(0, mem_total=bytes_to_human_readable(self.mem_total))

    def set_utl(self, utl: int):
        if utl < 0 or utl > 100:
            raise ValueError("utl must be 0 ~ 100")
        self.utl = utl
        self.progress_utl.update(0, completed=self.utl)

    # gpu mem used in bytes
    def set_mem_used(self, mem_used: int):
        if mem_used < 0:
            raise ValueError("mem_used must be positive")
        if mem_used > self.mem_total:
            raise ValueError("mem_used must be less than mem_total")
        self.mem_used = mem_used
        self.mem_free = self.mem_total - self.mem_used
        self.progress_mem.update(0, completed=self.mem_used, mem_used=bytes_to_human_readable(self.mem_used))
    
    def set_gpu_temperture(self, temperture: int):
        if temperture < 0:
            raise ValueError("temperture must be positive")
        self.temperture = temperture
    
    # in watts
    def set_power(self, power: int):
        if power < 0:
            raise ValueError("power must be positive")
        self.power = power
    
    def set_clocks(self, gpu_clocks: int, mem_clocks: int):
        if gpu_clocks < 0:
            raise ValueError("gpu_clocks must be positive")
        if gpu_clocks > self.gpu_clocks_max:
            raise ValueError("gpu_clocks must be less than gpu_clocks_max")
        if mem_clocks < 0:
            raise ValueError("mem_clocks must be positive")
        if mem_clocks > self.mem_clocks_max:
            raise ValueError("mem_clocks must be less than mem_clocks_max")
        self.gpu_clocks = gpu_clocks
        self.mem_clocks = mem_clocks
    
    # energy consumption in kJoule
    def set_energy(self, energy: int):
        if energy < 0:
            raise ValueError("energy must be positive")
        self.energy = energy
    
    def get_energy(self):
        return f"{self.energy:>9.2f}kJ"
    
    def get_progress_utl(self):
        return self.progress_utl
    
    def get_progress_mem(self):
        return self.progress_mem

    def get_id(self):
        return self.id
    
    def get_power(self):
        return f"{round(self.power, 1)}W"

    def get_temperture(self):
        return f"{self.temperture}°C"