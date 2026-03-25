"""Oracle CLI — training dataset generation and management."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()

# Default paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
GENERATED_DIR = DATA_DIR / "generated"
SOURCES_DIR = DATA_DIR / "sources"
EXPORTS_DIR = DATA_DIR / "exports"


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
def main(verbose: bool):
    """Oracle — Domain name industry training dataset generator."""
    setup_logging(verbose)


# -----------------------------------------------------------------------
# taxonomy
# -----------------------------------------------------------------------
@main.command()
@click.option("--stats", is_flag=True, help="Show topic counts per category")
@click.option("--category", "-c", default=None, help="Show details for a specific category")
def taxonomy(stats: bool, category: str | None):
    """Display the topic taxonomy."""
    from oracle.taxonomy import TAXONOMY, category_stats, get_category, topic_count

    if category:
        cat = get_category(category)
        if not cat:
            console.print(f"[red]Unknown category: {category}[/red]")
            available = [c.slug for c in TAXONOMY]
            console.print(f"Available: {', '.join(available)}")
            return

        console.print(f"\n[bold]{cat.name}[/bold] ({cat.slug})")
        console.print(f"  {cat.description}\n")

        for sub in cat.subcategories:
            console.print(f"  [cyan]{sub.name}[/cyan] ({sub.slug}) — {len(sub.topics)} topics")
            for topic in sub.topics:
                rfcs = f" [{', '.join(topic.rfcs)}]" if topic.rfcs else ""
                console.print(f"    • {topic.name}{rfcs}")
            console.print()
        return

    if stats:
        table = Table(title="Oracle Taxonomy Coverage")
        table.add_column("Category", style="cyan")
        table.add_column("Slug", style="dim")
        table.add_column("Subcategories", justify="right")
        table.add_column("Topics", justify="right")

        cs = category_stats()
        total_topics = 0
        total_subs = 0
        for cat_obj in TAXONOMY:
            s = cs[cat_obj.slug]
            table.add_row(cat_obj.name, cat_obj.slug, str(s["subcategories"]), str(s["topics"]))
            total_topics += s["topics"]
            total_subs += s["subcategories"]

        table.add_section()
        table.add_row("[bold]Total[/bold]", "", str(total_subs), str(total_topics))

        console.print(table)
        console.print(f"\n[green]{topic_count()} total topics across {len(TAXONOMY)} categories[/green]")
        return

    # Default: list categories
    for cat_obj in TAXONOMY:
        topic_total = sum(len(s.topics) for s in cat_obj.subcategories)
        console.print(f"  [cyan]{cat_obj.slug:20s}[/cyan] {cat_obj.name} ({topic_total} topics)")


# -----------------------------------------------------------------------
# generate
# -----------------------------------------------------------------------
@main.command()
@click.option("--category", "-c", required=True, help="Category slug to generate for")
@click.option("--difficulty", "-d", default="intermediate", type=click.Choice(["beginner", "intermediate", "advanced", "expert"]))
@click.option("--count", "-n", default=3, help="Examples per topic")
@click.option("--provider", "-p", default="anthropic", type=click.Choice(["anthropic", "openai", "ollama"]))
@click.option("--model", "-m", default=None, help="Model name override")
@click.option("--output", "-o", default=None, type=click.Path(), help="Output directory")
def generate(category: str, difficulty: str, count: int, provider: str, model: str | None, output: str | None):
    """Generate synthetic training data for a category."""
    from oracle.taxonomy import get_category

    cat = get_category(category)
    if not cat:
        console.print(f"[red]Unknown category: {category}[/red]")
        return

    output_dir = Path(output) if output else GENERATED_DIR

    from oracle.generators.synthetic import SyntheticGenerator

    gen = SyntheticGenerator(
        output_dir=output_dir,
        provider=provider,
        model=model,
    )

    topic_total = sum(len(s.topics) for s in cat.subcategories)
    console.print(
        f"\n[bold]Generating[/bold] {count} × {topic_total} topics = "
        f"~{count * topic_total} examples for [cyan]{cat.name}[/cyan] [{difficulty}]"
    )

    examples = asyncio.run(gen.generate_category(cat, difficulty, count))
    console.print(f"\n[green]Generated {len(examples)} examples → {output_dir}[/green]")


# -----------------------------------------------------------------------
# fetch-sources
# -----------------------------------------------------------------------
@main.command("fetch-sources")
@click.option("--type", "-t", "source_type", default="all", type=click.Choice(["rfc", "iana", "icann", "all"]))
@click.option("--output", "-o", default=None, type=click.Path(), help="Cache directory")
def fetch_sources(source_type: str, output: str | None):
    """Fetch and cache source documents (RFCs, IANA data, ICANN docs)."""
    cache_dir = Path(output) if output else SOURCES_DIR

    async def _fetch():
        fetched = 0

        if source_type in ("rfc", "all"):
            from oracle.sources.rfc import RfcFetcher, collect_taxonomy_rfcs

            rfc_fetcher = RfcFetcher(cache_dir / "rfcs")
            rfc_numbers = collect_taxonomy_rfcs()
            console.print(f"Fetching {len(rfc_numbers)} RFCs...")
            docs = await rfc_fetcher.fetch_batch(rfc_numbers)
            fetched += len(docs)
            console.print(f"  [green]Fetched {len(docs)} RFCs[/green]")

        if source_type in ("iana", "all"):
            from oracle.sources.iana import IanaFetcher

            iana_fetcher = IanaFetcher(cache_dir / "iana")
            data = await iana_fetcher.fetch_all()
            fetched += 1
            console.print(f"  [green]Fetched IANA data: {len(data.tld_list)} TLDs, {len(data.rr_types)} RR types[/green]")

        if source_type in ("icann", "all"):
            from oracle.sources.icann import IcannFetcher

            icann_fetcher = IcannFetcher(cache_dir / "icann")
            sources = icann_fetcher.list_available_sources()
            console.print(f"Fetching {len(sources)} ICANN/WIPO documents...")
            for src in sources:
                await icann_fetcher.fetch_document(src["key"])
            fetched += len(sources)
            console.print(f"  [green]Fetched {len(sources)} documents[/green]")

        return fetched

    total = asyncio.run(_fetch())
    console.print(f"\n[green]Done. {total} sources cached in {cache_dir}[/green]")


# -----------------------------------------------------------------------
# validate
# -----------------------------------------------------------------------
@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, help="Apply stricter quality thresholds")
def validate(path: str, strict: bool):
    """Validate a generated dataset file or directory."""
    from oracle.generators.base import BaseGenerator
    from oracle.validators.quality import validate_and_deduplicate

    target = Path(path)
    files = list(target.glob("*.jsonl")) if target.is_dir() else [target]

    all_examples = []
    for f in files:
        examples = BaseGenerator.load_examples(f)
        all_examples.extend(examples)
        console.print(f"  Loaded {len(examples)} from {f.name}")

    console.print(f"\n[bold]Validating {len(all_examples)} examples...[/bold]")
    result = validate_and_deduplicate(all_examples, strict=strict)

    table = Table(title="Validation Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right")

    table.add_row("Valid examples", f"[green]{len(result.valid)}[/green]")
    table.add_row("Rejected", f"[red]{len(result.rejected)}[/red]")
    table.add_row("Duplicates removed", str(result.duplicates_removed))
    table.add_row("Token counts set", str(result.token_counts_set))

    if result.valid:
        total_tokens = sum(e.token_count or 0 for e in result.valid)
        table.add_row("Total tokens", f"{total_tokens:,}")

    console.print(table)

    if result.rejected:
        console.print(f"\n[yellow]Top rejection reasons:[/yellow]")
        reasons: dict[str, int] = {}
        for _, reason in result.rejected:
            key = reason.split(":")[0] if ":" in reason else reason
            reasons[key] = reasons.get(key, 0) + 1
        for reason, count in sorted(reasons.items(), key=lambda x: -x[1])[:10]:
            console.print(f"  {count:4d}  {reason}")


# -----------------------------------------------------------------------
# export
# -----------------------------------------------------------------------
@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--format", "-f", "fmt", default="openai_chat", type=click.Choice(["openai_chat", "nemo_sft", "alpaca"]))
@click.option("--output", "-o", default=None, type=click.Path(), help="Output directory")
@click.option("--name", default="oracle-domain-expert", help="Dataset name")
@click.option("--version", default="0.1.0", help="Dataset version")
@click.option("--validate/--no-validate", default=True, help="Validate before export")
def export(path: str, fmt: str, output: str | None, name: str, version: str, validate: bool):
    """Export generated data to a training-ready format."""
    from oracle.exporters.nemo import export_with_metadata
    from oracle.generators.base import BaseGenerator
    from oracle.validators.quality import validate_and_deduplicate

    target = Path(path)
    files = list(target.glob("*.jsonl")) if target.is_dir() else [target]

    all_examples = []
    for f in files:
        examples = BaseGenerator.load_examples(f)
        all_examples.extend(examples)

    console.print(f"Loaded {len(all_examples)} examples from {len(files)} file(s)")

    if validate:
        result = validate_and_deduplicate(all_examples)
        all_examples = result.valid
        console.print(
            f"After validation: {len(all_examples)} valid "
            f"({result.duplicates_removed} dupes, {len(result.rejected)} rejected)"
        )

    output_dir = Path(output) if output else EXPORTS_DIR

    data_path, meta_path = export_with_metadata(
        examples=all_examples,
        output_dir=output_dir,
        export_format=fmt,
        name=name,
        version=version,
    )

    console.print(f"\n[green]Exported:[/green]")
    console.print(f"  Data:     {data_path}")
    console.print(f"  Metadata: {meta_path}")


# -----------------------------------------------------------------------
# stats
# -----------------------------------------------------------------------
@main.command()
@click.argument("path", type=click.Path(exists=True), default="data/generated")
def stats(path: str):
    """Show statistics for generated data."""
    from collections import Counter

    from oracle.generators.base import BaseGenerator
    from oracle.validators.quality import estimate_tokens

    target = Path(path)
    files = list(target.glob("*.jsonl")) if target.is_dir() else [target]

    if not files:
        console.print("[yellow]No JSONL files found[/yellow]")
        return

    all_examples = []
    for f in files:
        examples = BaseGenerator.load_examples(f)
        all_examples.extend(examples)

    if not all_examples:
        console.print("[yellow]No examples found[/yellow]")
        return

    # Category breakdown
    cat_counts = Counter(e.category for e in all_examples)
    diff_counts = Counter(e.difficulty for e in all_examples)
    fmt_counts = Counter(e.format.value for e in all_examples)

    total_tokens = sum(
        estimate_tokens(" ".join(m.content for m in e.messages))
        for e in all_examples
    )

    table = Table(title=f"Dataset Statistics ({len(all_examples)} examples)")
    table.add_column("Category", style="cyan")
    table.add_column("Examples", justify="right")
    for slug, count in cat_counts.most_common():
        table.add_row(slug, str(count))
    console.print(table)

    table2 = Table(title="By Difficulty")
    table2.add_column("Difficulty", style="cyan")
    table2.add_column("Count", justify="right")
    for diff, count in diff_counts.most_common():
        table2.add_row(diff, str(count))
    console.print(table2)

    console.print(f"\nTotal estimated tokens: [bold]{total_tokens:,}[/bold]")
    console.print(f"Avg tokens per example: [bold]{total_tokens // max(len(all_examples), 1):,}[/bold]")

    # Format breakdown
    if fmt_counts:
        table3 = Table(title="By Format")
        table3.add_column("Format", style="cyan")
        table3.add_column("Count", justify="right")
        for fmt, count in fmt_counts.most_common():
            table3.add_row(fmt, str(count))
        console.print(table3)


# -----------------------------------------------------------------------
# plan
# -----------------------------------------------------------------------
@main.command()
@click.option("--size", "-s", default="medium", type=click.Choice(["small", "medium", "large"]))
@click.option("--category", "-c", multiple=True, help="Specific categories (default: all)")
@click.option("--provider", "-p", default="anthropic", type=click.Choice(["anthropic", "openai", "ollama"]))
@click.option("--model", "-m", default=None, help="Model name override")
@click.option("--output", "-o", default=None, type=click.Path(), help="Output directory")
@click.option("--dry-run", is_flag=True, help="Show plan without executing")
def plan(size: str, category: tuple[str, ...], provider: str, model: str | None, output: str | None, dry_run: bool):
    """Execute a generation plan (small/medium/large)."""
    from oracle.plan import execute_plan, plan_large, plan_medium, plan_small
    from oracle.taxonomy import TAXONOMY, topic_count

    plans = {"small": plan_small, "medium": plan_medium, "large": plan_large}
    gen_plan = plans[size]()
    gen_plan.provider = provider
    if model:
        gen_plan.model = model

    cats = list(category) if category else [c.slug for c in TAXONOMY]
    total_topics = topic_count()

    console.print(f"\n[bold]Generation Plan: {size}[/bold]")
    console.print(f"  Topics: {total_topics}")
    console.print(f"  Per topic: ~{gen_plan.default_per_topic} examples")
    console.print(f"  Estimated total: ~{total_topics * gen_plan.default_per_topic:,} examples")
    console.print(f"  Categories: {len(cats)}")
    console.print(f"  Provider: {provider}")
    console.print(f"  Difficulty: {gen_plan.default_difficulty}")
    console.print(f"  Format: {gen_plan.default_format}")

    if dry_run:
        console.print("\n[yellow]Dry run — no examples generated[/yellow]")
        return

    output_dir = Path(output) if output else GENERATED_DIR
    results = asyncio.run(execute_plan(gen_plan, output_dir, cats))

    total = sum(results.values())
    console.print(f"\n[green]Generated {total:,} examples across {len(results)} categories[/green]")
    for cat_slug, count in sorted(results.items()):
        console.print(f"  {cat_slug}: {count}")


# -----------------------------------------------------------------------
# export-splits
# -----------------------------------------------------------------------
@main.command("export-splits")
@click.argument("path", type=click.Path(exists=True))
@click.option("--format", "-f", "fmt", default="openai_chat", type=click.Choice(["openai_chat", "nemo_sft", "alpaca"]))
@click.option("--output", "-o", default=None, type=click.Path(), help="Output directory")
@click.option("--name", default="oracle-domain-expert", help="Dataset name")
@click.option("--version", default="0.1.0", help="Dataset version")
@click.option("--train-ratio", default=0.85, type=float, help="Training set ratio")
@click.option("--val-ratio", default=0.10, type=float, help="Validation set ratio")
@click.option("--test-ratio", default=0.05, type=float, help="Test set ratio")
@click.option("--seed", default=42, type=int, help="Random seed for reproducibility")
@click.option("--validate/--no-validate", default=True, help="Validate before export")
def export_splits(
    path: str, fmt: str, output: str | None, name: str, version: str,
    train_ratio: float, val_ratio: float, test_ratio: float, seed: int, validate: bool,
):
    """Export with train/validation/test splits."""
    from oracle.exporters.nemo import export_splits as do_export_splits
    from oracle.generators.base import BaseGenerator
    from oracle.validators.quality import validate_and_deduplicate

    target = Path(path)
    files = list(target.glob("*.jsonl")) if target.is_dir() else [target]

    all_examples = []
    for f in files:
        all_examples.extend(BaseGenerator.load_examples(f))

    console.print(f"Loaded {len(all_examples)} examples from {len(files)} file(s)")

    if validate:
        result = validate_and_deduplicate(all_examples)
        all_examples = result.valid
        console.print(
            f"After validation: {len(all_examples)} valid "
            f"({result.duplicates_removed} dupes, {len(result.rejected)} rejected)"
        )

    output_dir = Path(output) if output else EXPORTS_DIR

    paths = do_export_splits(
        examples=all_examples,
        output_dir=output_dir,
        export_format=fmt,
        name=name,
        version=version,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
        seed=seed,
    )

    console.print(f"\n[green]Exported splits:[/green]")
    for split_name, split_path in paths.items():
        console.print(f"  {split_name}: {split_path}")


# -----------------------------------------------------------------------
# augment
# -----------------------------------------------------------------------
@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--count", "-n", default=2, help="Paraphrases per example")
@click.option("--provider", "-p", default="anthropic", type=click.Choice(["anthropic", "openai", "ollama"]))
@click.option("--model", "-m", default=None, help="Model name override")
@click.option("--output", "-o", default=None, type=click.Path(), help="Output file")
def augment(path: str, count: int, provider: str, model: str | None, output: str | None):
    """Augment dataset with paraphrased questions."""
    from oracle.augment import paraphrase_questions
    from oracle.generators.base import BaseGenerator

    target = Path(path)
    files = list(target.glob("*.jsonl")) if target.is_dir() else [target]

    all_examples = []
    for f in files:
        all_examples.extend(BaseGenerator.load_examples(f))

    console.print(f"Loaded {len(all_examples)} examples, generating {count} paraphrases each...")

    augmented = asyncio.run(
        paraphrase_questions(all_examples, provider=provider, model=model, paraphrases_per_example=count)
    )

    output_path = Path(output) if output else (GENERATED_DIR / "augmented.jsonl")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for ex in augmented:
            f.write(ex.model_dump_json() + "\n")

    console.print(f"\n[green]Generated {len(augmented)} augmented examples → {output_path}[/green]")


if __name__ == "__main__":
    main()
