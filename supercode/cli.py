"""
Command Line Interface for Supercode with Interactive Aquarium
"""

import argparse
import sys
import time
from . import __version__
from .main import run
from .ui import (
    display_welcome,
    display_loading,
    display_success,
    display_error,
    display_command_output,
    show_menu,
    console
)


def interactive_mode():
    """Modo interativo com interface gráfica"""
    
    display_welcome()
    time.sleep(1)
    
    while True:
        try:
            console.print("\n[cyan]Escolha uma opção:[/cyan]")
            console.print("[yellow]1[/yellow] - Run")
            console.print("[yellow]2[/yellow] - Info")
            console.print("[yellow]3[/yellow] - Help")
            console.print("[yellow]4[/yellow] - Exit")
            console.print()
            
            choice = console.input("[bold cyan]supercode > [/bold cyan]").strip()
            
            if choice == "1":
                display_loading("Executando comando")
                time.sleep(1)
                result = run()
                if result == 0:
                    display_success("Comando executado com sucesso!")
                else:
                    display_error("Erro ao executar comando")
                time.sleep(2)
                
            elif choice == "2":
                display_command_output(
                    "Informações do Sistema",
                    f"""
Supercode v{__version__}
Python Interactive Command Interface
Mascote: 🐠 Peixe no Aquário

Status: ✓ Online
Modo: Interativo com Interface Gráfica
                    """.strip()
                )
                time.sleep(2)
                
            elif choice == "3":
                display_command_output(
                    "Ajuda",
                    """
Supercode - Interactive Command Interface

Comandos disponíveis:
  1 - Run       : Executa a aplicação
  2 - Info      : Mostra informações do sistema
  3 - Help      : Exibe esta ajuda
  4 - Exit      : Sai da aplicação

Uso via terminal:
  supercode                 : Modo interativo (padrão)
  supercode --verbose       : Modo com saída detalhada
  supercode --version       : Mostra a versão
  supercode --help          : Mostra ajuda
                    """.strip()
                )
                time.sleep(2)
                
            elif choice == "4":
                display_success("Até logo! 🐠")
                time.sleep(1)
                break
                
            else:
                display_error("Opção inválida! Escolha 1, 2, 3 ou 4")
                time.sleep(1)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrompido pelo usuário[/yellow]")
            break
        except Exception as e:
            display_error(f"Erro: {str(e)}")
            time.sleep(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="🐠 Supercode - Interactive Command Interface with Aquarium",
        prog="supercode"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run without interactive interface"
    )
    
    args = parser.parse_args()
    
    # Se non-interactive, executa modo simples
    if args.non_interactive:
        if args.verbose:
            console.print(f"[cyan]Supercode v{__version__}[/cyan]")
            console.print("[cyan]Verbose mode enabled[/cyan]")
        return run()
    
    # Senão, executa modo interativo com interface gráfica
    try:
        interactive_mode()
        return 0
    except Exception as e:
        display_error(f"Erro fatal: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
