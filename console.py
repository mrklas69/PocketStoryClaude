import sys
import time
from pathlib import Path
from collections import deque

from rich.columns import Columns
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich.tree import Tree
from rich.text import Text

from backend.core.entity import Entity, EntityType
from backend.core.relation import RelationType
from backend.core.world import World
from backend.sim.engine import tick

console = Console()

TYPE_STYLE = {
    EntityType.CHAR:   "[bold cyan]CHAR[/]",
    EntityType.ENVI:   "[bold blue]ENVI[/]",
    EntityType.UNIQUE: "[bold magenta]UNI[/]",
    EntityType.SUMS:   "[bold white]SUMS[/]",
}

_TYPE_ORDER = [t.value for t in EntityType]  # canonical display order: CHAR, ENVI, UNIQUE, SUMS

HP_BAR_WIDTH = 10
LOG_LINES    = 8


def _hp_bar(hp: int, hp_max: int) -> str:
    ratio  = hp / hp_max if hp_max > 0 else 0
    filled = round(ratio * HP_BAR_WIDTH)
    bar    = "#" * filled + "." * (HP_BAR_WIDTH - filled)
    colour = "green" if ratio > 0.5 else ("yellow" if ratio > 0.25 else "red")
    return f"[{colour}]{bar}[/] {hp}/{hp_max}"


def _signed(n: int) -> str:
    return f"+{n}" if n >= 0 else str(n)



def label(e: Entity, count: int = 1, full: bool = False, loc_hp: int | None = None) -> str:
    tag   = TYPE_STYLE[e.type]
    extra = f"  x{count}" if e.type == EntityType.SUMS else ""
    # SUMS: HP lives on the LOCATION relation (loc_hp); others: on the entity
    effective_hp = loc_hp if e.type == EntityType.SUMS else e.hp
    hp    = f"  {_hp_bar(effective_hp, e.hp_max)}" if effective_hp is not None and e.hp_max is not None else ""

    details = ""
    if full:
        details += f"  [dim]r{e.rank}[/]"
        if e.nature is not None:
            details += f"  [dim]nat:{_signed(e.nature)}[/]"
        if e.karma is not None:
            details += f"  [dim]karma:{_signed(e.karma)}[/]"

    return f"{tag}  {e.name}{extra}{hp}{details}"


def add_children(world: World, parent_id: str, node: Tree, full: bool) -> None:
    for child, count in world.children(parent_id):
        loc_hp = None
        if child.type == EntityType.SUMS:
            loc_rel = next(
                (r for r in world.relations.values()
                 if r.type == RelationType.LOCATION and r.ent1 == parent_id and r.ent2 == child.id),
                None,
            )
            if loc_rel is not None:
                loc_hp = loc_rel.hp
        child_node = node.add(label(child, count, full, loc_hp=loc_hp))
        add_children(world, child.id, child_node, full)


def _build_manifest_panel(world: World) -> Panel:
    """Header panel shown only in --full mode."""
    mf = world.manifest
    m  = world.meta

    # Stats computed on the fly
    from collections import Counter
    type_counts = Counter(e.type.value for e in world.entities.values())
    rel_counts  = Counter(r.type.value for r in world.relations.values())

    stats = "  ".join(
        f"[dim]{k}:[/] {v}"
        for k, v in sorted(type_counts.items(), key=lambda x: _TYPE_ORDER.index(x[0]) if x[0] in _TYPE_ORDER else 99)
    ) + "   " + "  ".join(
        f"[dim]{k}:[/] {v}"
        for k, v in sorted(rel_counts.items())
    )

    lines: list = []
    if mf.author or mf.created:
        meta_line = Text()
        if mf.author:
            meta_line.append(f"by {mf.author}", style="bold")
        if mf.created:
            meta_line.append(f"  {mf.created}", style="dim")
        meta_line.append(f"  v{mf.version}", style="dim")
        if m.turn:
            meta_line.append(f"  turn: {m.turn}", style="yellow")
        lines.append(meta_line)
    if mf.lore:
        lines.append(Text(mf.lore, style="italic dim"))
    lines.append(Text.from_markup(stats))

    return Panel(
        Group(*lines),
        title=f"[bold]{world.name}[/]",
        subtitle=f"[dim]{world.description}[/]" if world.description else "",
        border_style="cyan",
    )


def build_display(world: World, tick_num: int, log: deque, full: bool) -> Group:
    """Build the full renderable for one Live refresh."""
    # ── World tree ───────────────────────────────────────────────
    roots = world.roots()
    if not full:
        roots = [r for r in roots if r.type != EntityType.UNIQUE]
    if len(roots) == 1:
        tree = Tree(label(roots[0], full=full))
        add_children(world, roots[0].id, tree, full)
    else:
        tree = Tree("[bold]World[/]")
        for root in roots:
            subtree = tree.add(label(root, full=full))
            add_children(world, root.id, subtree, full)

    world_panel = Panel(
        tree,
        title=f"[bold]{world.name}[/]  [dim]tick {tick_num}[/]",
        subtitle=f"[dim]{world.description}[/]" if world.description and not full else "",
        border_style="blue",
    )

    # ── Event log ────────────────────────────────────────────────
    if log:
        log_text = Text("\n".join(log), style="dim")
    else:
        log_text = Text("(no events yet)", style="dim italic")

    log_panel = Panel(log_text, title="[dim]Event log[/]", border_style="dim")

    if full:
        return Group(_build_manifest_panel(world), world_panel, log_panel)
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
