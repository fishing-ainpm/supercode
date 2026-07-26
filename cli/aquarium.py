"""
cli/aquarium.py

Aquário em ASCII puro, rodando no terminal via curses. Peixinho vermelho
(mesmo bicho da mascote do SuperCode) nadando de um lado pro outro,
bolhas subindo, planta balançando. Usado como splash/idle screen do CLI
(`supercode aquarium` ou exibido enquanto os agentes pensam).

Sem HTML, sem browser — 100% terminal.
"""

from __future__ import annotations

import curses
import random
import time

# peixe desenhado em ASCII, voltado pra direita. A versão voltada pra
# esquerda é gerada espelhando a string na hora de desenhar.
FISH_RIGHT = [
    r"     __",
    r"    /  \_",
    r"><(('>  )",
    r"    \__/",
]

BUBBLE_CHARS = [".", "o", "O", "°"]
SAND_CHARS = ["_", ".", "-", "_", "_", "."]


class Bubble:
    __slots__ = ("x", "y", "char", "speed")

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.char = random.choice(BUBBLE_CHARS)
        self.speed = random.uniform(0.15, 0.4)

    def step(self):
        self.y -= self.speed


class Fish:
    def __init__(self, x: float, y: int, direction: int, speed: float):
        self.x = x
        self.y = y
        self.direction = direction  # 1 = direita, -1 = esquerda
        self.speed = speed
        self.target_y = y
        self.frame = 0

    def step(self, width: int, height: int):
        self.x += self.speed * self.direction
        margin = len(FISH_RIGHT[0]) + 2
        if self.x >= width - margin:
            self.direction = -1
        elif self.x <= margin:
            self.direction = 1

        if random.random() < 0.01:
            self.target_y = random.randint(2, max(2, height - 6))
        if self.y < self.target_y:
            self.y += 1
        elif self.y > self.target_y:
            self.y -= 1

        self.frame += 1


def render_fish(stdscr, fish: Fish, color_pair: int):
    lines = FISH_RIGHT if fish.direction == 1 else [ln[::-1] for ln in FISH_RIGHT]
    x0 = int(fish.x)
    for i, ln in enumerate(lines):
        y = fish.y + i
        try:
            stdscr.addstr(y, x0, ln, curses.color_pair(color_pair))
        except curses.error:
            pass  # borda da tela, ignora


def render_plant(stdscr, x: int, base_y: int, height: int, t: float, color_pair: int):
    for h in range(height):
        sway = int(2 * (0.5 + 0.5 * _sin(t / 3 + h * 0.5)))
        y = base_y - h
        cx = x + sway
        ch = "(" if sway == 0 else (")" if sway == 1 else "|")
        try:
            stdscr.addstr(y, cx, ch, curses.color_pair(color_pair))
        except curses.error:
            pass


def _sin(v: float) -> float:
    # seno sem depender de math pra manter o módulo enxuto
    import math
    return math.sin(v)


def run_aquarium(stdscr, task_label: str | None = None, duration: float | None = None):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)      # peixe
    curses.init_pair(2, curses.COLOR_GREEN, -1)    # planta
    curses.init_pair(3, curses.COLOR_CYAN, -1)     # bolhas
    curses.init_pair(4, curses.COLOR_YELLOW, -1)   # areia
    curses.init_pair(5, curses.COLOR_WHITE, -1)    # texto/status

    height, width = stdscr.getmaxyx()
    fish = Fish(x=width // 2, y=height // 2, direction=1, speed=0.6)
    bubbles: list[Bubble] = []

    plants = [
        (max(2, width // 8), height - 2, min(6, height - 4)),
        (width - max(4, width // 6), height - 2, min(5, height - 4)),
    ]

    start = time.time()
    last_spawn = 0.0
    frame = 0

    while True:
        now = time.time()
        if duration and (now - start) > duration:
            break

        # sai com 'q' ou ESC
        ch = stdscr.getch()
        if ch in (ord("q"), 27):
            break

        stdscr.erase()
        height, width = stdscr.getmaxyx()

        # areia no fundo
        for x in range(0, width, 1):
            if random.random() < 0.15:
                ch_s = SAND_CHARS[(x + frame // 20) % len(SAND_CHARS)]
                try:
                    stdscr.addstr(height - 1, x, ch_s, curses.color_pair(4))
                except curses.error:
                    pass

        # plantas
        for (px, base_y, h) in plants:
            render_plant(stdscr, px, base_y - 1, h, now, 2)

        # bolhas
        if now - last_spawn > 0.6:
            bubbles.append(Bubble(x=random.uniform(3, width - 3), y=height - 2))
            last_spawn = now
        for b in bubbles:
            b.step()
        bubbles[:] = [b for b in bubbles if b.y > 0]
        for b in bubbles:
            try:
                stdscr.addstr(int(b.y), int(b.x), b.char, curses.color_pair(3))
            except curses.error:
                pass

        # peixe
        fish.step(width, height)
        render_fish(stdscr, fish, 1)

        # status
        label = task_label or "supercode aquarium — 'q' pra sair"
        try:
            stdscr.addstr(0, 0, label[: max(0, width - 1)], curses.color_pair(5) | curses.A_DIM)
        except curses.error:
            pass

        stdscr.refresh()
        time.sleep(0.06)
        frame += 1


def main(task_label: str | None = None, duration: float | None = None):
    """Entrypoint público — chamado por cli/main.py."""
    curses.wrapper(lambda stdscr: run_aquarium(stdscr, task_label, duration))


if __name__ == "__main__":
    main()
