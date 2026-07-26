"""
Rich UI components for Supercode
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
import time
import random

console = Console()


def build_startup_banner() -> str:
    """Retorna um banner inicial com peixe ASCII, barra de comando e mensagem de entrada."""
    fish = [
        "      <><((('>      ",
        "      /\\_\\_\\       ",
        "      \\__//        ",
    ]
    command_bar = "[ CMD ] supercode  ──> digite sua tarefa"
    ascii_art = "\n".join(fish)
    return f"""
🐠  SUPERCODE  🐠
{ascii_art}

{command_bar}

Digite sua tarefa e pressione Enter.
"""


class Fish:
    """Mascote peixe animado"""
    
    def __init__(self):
        self.position = 0
        self.direction = 1
        self.fishes = ["🐠", "🐟", "🐡"]
        self.current_fish = random.choice(self.fishes)
    
    def animate(self):
        """Retorna frames animados do peixe"""
        frames = []
        max_width = 50
        
        for i in range(max_width):
            line = " " * i + self.current_fish
            frames.append(line)
        
        return frames
    
    def get_fish(self):
        """Retorna o peixe atual"""
        return self.current_fish
    
    def change_fish(self):
        """Muda o tipo de peixe"""
        self.current_fish = random.choice(self.fishes)


class Aquarium:
    """Aquário com interface interativa"""
    
    def __init__(self):
        self.fish = Fish()
        self.width = 70
        self.height = 15
    
    def draw_aquarium(self, command_text="", progress=0):
        """Desenha o aquário com peixe animado"""
        
        # Topo do aquário
        top = "╔" + "═" * (self.width - 2) + "╗"
        
        # Linhas do aquário com bubbles e peixe
        lines = []
        middle = self.height // 2
        
        for i in range(self.height):
            if i == middle:
                # Linha com o peixe
                fish_pos = int((self.width - 2) * (progress / 100)) if progress > 0 else 10
                line_content = " " * fish_pos + self.fish.get_fish() + " " * (self.width - fish_pos - 3)
                lines.append("║" + line_content + "║")
            elif i % 3 == 0:
                # Linhas com bubbles
                bubbles = ""
                for _ in range(random.randint(2, 4)):
                    bubble_pos = random.randint(1, self.width - 2)
                    if bubble_pos < len(bubbles):
                        continue
                    bubbles = " " * bubble_pos + "○"
                line_content = bubbles.ljust(self.width - 2)
                lines.append("║" + line_content + "║")
            else:
                line_content = " " * (self.width - 2)
                lines.append("║" + line_content + "║")
        
        # Base do aquário
        bottom = "╚" + "═" * (self.width - 2) + "╝"
        
        # Retorna o aquário como string
        aquarium_str = top + "\n"
        aquarium_str += "\n".join(lines)
        aquarium_str += "\n" + bottom
        
        return aquarium_str
    
    def show_command_bar(self, command_text="", progress=0):
        """Mostra a barra de comando e progresso"""
        
        bar_width = self.width - 6
        filled = int(bar_width * progress / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        
        info = f"[{bar}] {progress}%"
        
        return info


def display_welcome():
    """Exibe a tela de boas-vindas"""

    console.clear()

    banner = build_startup_banner()
    console.print(Panel.fit(banner, border_style="cyan", title="[bold green]Bem-vindo[/bold green]"))
    console.print()
    console.print("[bold magenta]Seu peixe está pronto para ajudar.[/bold magenta]")
    console.print("[yellow]Digite sua tarefa diretamente e pressione Enter.[/yellow]")
    console.print()


def display_loading(message="Processando"):
    """Exibe animação de carregamento"""
    
    aquarium = Aquarium()
    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    for i in range(50):
        progress = (i / 50) * 100
        
        aquarium_display = aquarium.draw_aquarium(progress=int(progress))
        info = aquarium.show_command_bar(message, int(progress))
        
        console.clear()
        
        title = Text("🐠 SUPERCODE 🐠", justify="center", style="bold cyan")
        console.print("\n")
        console.print(title)
        console.print("\n")
        
        panel = Panel(
            aquarium_display + "\n\n" + info,
            title=f"[bold green]{message}... {spinner[i % len(spinner)]}[/bold green]",
            border_style="green",
            expand=True
        )
        console.print(panel)
        
        time.sleep(0.05)


def display_success(message="Comando executado com sucesso!"):
    """Exibe mensagem de sucesso"""
    
    console.clear()
    
    title = Text("🐠 SUPERCODE 🐠", justify="center", style="bold cyan")
    console.print("\n")
    console.print(title)
    console.print("\n")
    
    aquarium = Aquarium()
    # Muda o peixe para celebração
    aquarium.fish.current_fish = "🐠✨"
    aquarium_display = aquarium.draw_aquarium(progress=100)
    info = aquarium.show_command_bar("Completo", 100)
    
    panel = Panel(
        aquarium_display + "\n\n" + info + "\n\n" + 
        Text(message, justify="center", style="bold green"),
        title="[bold green]✓ Sucesso[/bold green]",
        border_style="green",
        expand=True
    )
    console.print(panel)
    
    console.print("\n")


def display_error(message="Erro ao executar comando"):
    """Exibe mensagem de erro"""
    
    console.clear()
    
    title = Text("🐠 SUPERCODE 🐠", justify="center", style="bold cyan")
    console.print("\n")
    console.print(title)
    console.print("\n")
    
    aquarium = Aquarium()
    aquarium.fish.current_fish = "🐠💔"
    aquarium_display = aquarium.draw_aquarium(progress=0)
    
    panel = Panel(
        aquarium_display + "\n\n" + 
        Text(message, justify="center", style="bold red"),
        title="[bold red]✗ Erro[/bold red]",
        border_style="red",
        expand=True
    )
    console.print(panel)
    
    console.print("\n")


def display_command_output(title, output, command=""):
    """Exibe saída de comando com aquário"""
    
    console.clear()
    
    header = Text("🐠 SUPERCODE 🐠", justify="center", style="bold cyan")
    console.print("\n")
    console.print(header)
    console.print("\n")
    
    # Exibe comando executado
    if command:
        cmd_panel = Panel(
            Text(f"$ {command}", style="yellow"),
            title="[bold blue]Comando[/bold blue]",
            border_style="blue"
        )
        console.print(cmd_panel)
    
    # Exibe saída
    output_panel = Panel(
        Text(output, style="white"),
        title=f"[bold green]{title}[/bold green]",
        border_style="green"
    )
    console.print(output_panel)
    
    console.print("\n")


def show_menu():
    """Exibe menu de opções"""
    
    console.clear()
    
    title = Text("🐠 SUPERCODE - Menu Principal 🐠", justify="center", style="bold cyan")
    console.print("\n")
    console.print(title)
    console.print("\n")
    
    aquarium = Aquarium()
    aquarium_display = aquarium.draw_aquarium()
    
    table = Table(title="[bold]Opções Disponíveis[/bold]", box=box.ROUNDED)
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Opção", style="magenta")
    table.add_column("Descrição", style="green")
    
    table.add_row("1", "Run", "Executar código")
    table.add_row("2", "Info", "Informações do sistema")
    table.add_row("3", "Help", "Ajuda")
    table.add_row("4", "Exit", "Sair")
    
    panel = Panel(
        aquarium_display + "\n\n",
        title="[bold green]Aquário Supercode[/bold green]",
        border_style="blue",
        expand=True
    )
    console.print(panel)
    console.print("\n")
    console.print(table)
    console.print("\n")
