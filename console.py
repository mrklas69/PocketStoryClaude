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
from backend.core.relation import RelationType
from backend.core.world import World
from backend.sim.tick import tick

console = Console()

TYPE_STYLE = {
    EntityType.ENVI:   "[bold blue]ENVI[/]",
    EntityType.CHAR:   "[bold cyan]CHAR[/]",
    EntityType.UNIQUE: "[bold magenta]UNIQUE[/]",
    EntityType.SUMS:   "[bold white]SUMS[/]",
}

HP_BAR_WIDTH = 10
LOG_LINES    = 8


def _hp_bar(hp: int, hp_max: int) -> str:
    ratio  = hp / hp_max if hp_max > 0 else 0
    filled = round(ratio * HP_BAR_WIDTH)
    bar    = "#" * filled + "." * (HP_BAR_WIDTH - filled)
    colour = "green" if ratio > 0.5 else ("yellow" if ratio > 0.25 else "red")
    return f"[{colour}][{bar}][/] {hp}/{hp_max}"


def _signed(n: int) -> str:
    return f"+{n}" if n >= 0 else str(n)


def _archetype_desc(world: World, entity_id: str) -> str | None:
    """Return description from entity itself, or from its first TYPE_OF archetype."""
    entity = world.get(entity_id)
    if entity is None:
        return None
    if entity.description:
        return entity.description
    for r in world.relations.values():
        if r.type == RelationType.TYPE_OF and r.ent1 == entity_id and r.ent2 is not None:
            archetype = world.get(r.ent2)
            if archetype and archetype.description:
                return archetype.description
    return None


def label(e: Entity, count: int = 1, full: bool = False, desc: str | None = None) -> str:
    tag   = TYPE_STYLE[e.type]
    extra = f"  x{count}" if e.type == EntityType.SUMS else ""
    hp    = f"  {_hp_bar(e.hp, e.hp_max)}" if e.hp is not None and e.hp_max is not None else ""

    details = ""
    if full:
        details += f"  [dim]r:{e.rank}[/]"
        if e.nature is not None:
            details += f"  [dim]nat:{_signed(e.nature)}[/]"
        if e.karma is not None:
            details += f"  [dim]karma:{_signed(e.karma)}[/]"
        if desc:
            short = (desc[:50] + "…") if len(desc) > 50 else desc
            details += f"  [dim italic]\"{short}\"[/]"

    return f"{tag}  {e.name}{extra}{hp}{details}"


def add_children(world: World, parent_id: str, node: Tree, full: bool) -> None:
    for child, count in world.children(parent_id):
        desc = _archetype_desc(world, child.id) if full else None
        child_node = node.add(label(child, count, full, desc))
        add_children(world, child.id, child_node, full)


def build_display(world: World, tick_num: int, log: deque, full: bool) -> Group:
    """Build the full renderable for one Live refresh."""
    # ── World tree ───────────────────────────────────────────────
    roots = world.roots()
    if not full:
        roots = [r for r in roots if r.type != EntityType.UNIQUE]
    if len(roots) == 1:
        desc = _archetype_desc(world, roots[0].id) if full else None
        tree = Tree(label(roots[0], full=full, desc=desc))
        add_children(world, roots[0].id, tree, full)
    else:
        tree = Tree("[bold]World[/]")
        for root in roots:
            desc = _archetype_desc(world, root.id) if full else None
            subtree = tree.add(label(root, full=full, desc=desc))
            add_children(world, root.id, subtree, full)

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


def parse_args() -> tuple[Path, int, float, bool]:
    """Returns (world_path, ticks, delay_seconds, full_mode)."""
    path  = Path("worlds/polar_night.json")
    ticks = 0
    delay = 0.8
    full  = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--ticks" and i + 1 < len(args):
            ticks = int(args[i + 1])
            i += 2
        elif args[i] == "--delay" and i + 1 < len(args):
            delay = float(args[i + 1])
            i += 2
        elif args[i] == "--full":
            full = True
            i += 1
        else:
            path = Path(args[i])
            i += 1

    return path, ticks, delay, full


if __name__ == "__main__":
    path, num_ticks, delay, full = parse_args()
    world  = World.load(path)
    log    = deque(maxlen=LOG_LINES)

    if num_ticks == 0:
        # Static view — no live loop
        console.print(build_display(world, 0, log, full))
    else:
        with Live(build_display(world, 0, log, full), console=console, refresh_per_second=4) as live:
            for t in range(1, num_ticks + 1):
                time.sleep(delay)
                events = tick(world)
                for msg in events:
                    log.append(f"[tick {t:>3}] {msg}")
                live.update(build_display(world, t, log, full))
