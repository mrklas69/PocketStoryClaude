import sys
import time
from pathlib import Path
from collections import deque

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text

from backend.core.entity import Entity, EntityType
from backend.core.world import World
from backend.sim.tick import tick

console = Console()

TYPE_STYLE = {
    EntityType.ENVI:   "[bold blue]ENVI[/]",
    EntityType.CHAR:   "[bold green]CHAR[/]",
    EntityType.UNIQUE: "[bold yellow]UNIQUE[/]",
    EntityType.SUMS:   "[bold magenta]SUMS[/]",
}

HP_BAR_WIDTH = 10
LOG_LINES    = 8   # how many recent log entries to keep


def _hp_bar(hp: int, hp_max: int) -> str:
    ratio  = hp / hp_max if hp_max > 0 else 0
    filled = round(ratio * HP_BAR_WIDTH)
    bar    = "#" * filled + "." * (HP_BAR_WIDTH - filled)
    colour = "green" if ratio > 0.5 else ("yellow" if ratio > 0.25 else "red")
    return f"[{colour}][{bar}][/] {hp}/{hp_max}"


def label(e: Entity, count: int = 1) -> str:
    tag   = TYPE_STYLE[e.type]
    extra = f"  x{count}" if e.type == EntityType.SUMS else ""
    cap   = f"  (cap: {e.capacity})" if e.type == EntityType.ENVI and e.capacity else ""
    hp    = f"  {_hp_bar(e.hp, e.hp_max)}" if e.hp is not None and e.hp_max is not None else ""
    return f"{tag}  {e.name}{extra}{cap}{hp}"


def add_children(world: World, parent_id: str, node: Tree) -> None:
    for child, count in world.children(parent_id):
        child_node = node.add(label(child, count))
        add_children(world, child.id, child_node)


def build_display(world: World, tick_num: int, log: deque) -> Group:
    """Build the full renderable for one Live refresh."""
    # ── World tree ───────────────────────────────────────────────
    roots = world.roots()
    if len(roots) == 1:
        tree = Tree(label(roots[0]))
        add_children(world, roots[0].id, tree)
    else:
        tree = Tree("[bold]World[/]")
        for root in roots:
            subtree = tree.add(label(root))
            add_children(world, root.id, subtree)

    world_panel = Panel(
        tree,
        title=f"[bold]{world.name}[/]  [dim]tick {tick_num}[/]",
        subtitle=f"[dim]{world.description}[/]" if world.description else "",
        border_style="blue",
    )

    # ── Event log ────────────────────────────────────────────────
    if log:
        log_text = Text("\n".join(log), style="dim")
    else:
        log_text = Text("(no events yet)", style="dim italic")

    log_panel = Panel(log_text, title="[dim]Event log[/]", border_style="dim")

    return Group(world_panel, log_panel)


def parse_args() -> tuple[Path, int, float]:
    """Returns (world_path, ticks, delay_seconds)."""
    path  = Path("worlds/martian_saga.json")
    ticks = 0
    delay = 0.8

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--ticks" and i + 1 < len(args):
            ticks = int(args[i + 1])
            i += 2
        elif args[i] == "--delay" and i + 1 < len(args):
            delay = float(args[i + 1])
            i += 2
        else:
            path = Path(args[i])
            i += 1

    return path, ticks, delay


if __name__ == "__main__":
    path, num_ticks, delay = parse_args()
    world  = World.load(path)
    log    = deque(maxlen=LOG_LINES)

    if num_ticks == 0:
        # Static view — no live loop
        console.print(build_display(world, 0, log))
    else:
        with Live(build_display(world, 0, log), console=console, refresh_per_second=4) as live:
            for t in range(1, num_ticks + 1):
                time.sleep(delay)
                events = tick(world)
                for msg in events:
                    log.append(f"[tick {t:>3}] {msg}")
                live.update(build_display(world, t, log))
