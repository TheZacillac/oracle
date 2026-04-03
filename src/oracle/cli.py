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
    try:
        from arcanum._logging import configure_logging
        import os
        if verbose:
            os.environ["ARCANUM_LOG_LEVEL"] = "DEBUG"
        configure_logging("oracle")
    except ImportError:
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
@click.option("--format", "-f", "format_type", default="instruction",
              type=click.Choice(["instruction", "multi_turn", "scenario", "tool_use"]),
              help="Training data format")
@click.option("--provider", "-p", default="anthropic", type=click.Choice(["anthropic", "openai", "ollama"]))
@click.option("--model", "-m", default=None, help="Model name override")
@click.option("--output", "-o", default=None, type=click.Path(), help="Output directory")
def generate(category: str, difficulty: str, count: int, format_type: str, provider: str, model: str | None, output: str | None):
    """Generate synthetic training data for a category."""
    from oracle.schema import ExampleFormat
    from oracle.taxonomy import get_category

    cat = get_category(category)
    if not cat:
        console.print(f"[red]Unknown category: {category}[/red]")
        return

    output_dir = Path(output) if output else GENERATED_DIR
    fmt = ExampleFormat(format_type)

    topic_total = sum(len(s.topics) for s in cat.subcategories)
    console.print(
        f"\n[bold]Generating[/bold] {count} × {topic_total} topics = "
        f"~{count * topic_total} {format_type} examples for [cyan]{cat.name}[/cyan] [{difficulty}]"
    )

    if fmt == ExampleFormat.TOOL_USE:
        from oracle.generators.tool_use import ToolUseGenerator

        gen = ToolUseGenerator(
            output_dir=output_dir,
            provider=provider,
            model=model,
        )
        async def _run_tool_use():
            all_ex = []
            for sub in cat.subcategories:
                for topic in sub.topics:
                    examples = await gen.generate(cat, sub, topic, difficulty, count)
                    gen.save_examples(examples)
                    all_ex.extend(examples)
            return all_ex

        all_examples = asyncio.run(_run_tool_use())
        console.print(f"\n[green]Generated {len(all_examples)} tool-use examples → {output_dir}[/green]")
    else:
        from oracle.generators.synthetic import SyntheticGenerator

        gen = SyntheticGenerator(
            output_dir=output_dir,
            provider=provider,
            model=model,
        )
        examples = asyncio.run(gen.generate_category(cat, difficulty, count, format_type=fmt))
        console.print(f"\n[green]Generated {len(examples)} examples → {output_dir}[/green]")


# -----------------------------------------------------------------------
# fetch-sources
# -----------------------------------------------------------------------
@main.command("fetch-sources")
@click.option(
    "--type", "-t", "source_type", default="all",
    type=click.Choice(["rfc", "iana", "icann", "cabforum", "psl", "industry", "governance", "dns-software", "all"]),
)
@click.option("--output", "-o", default=None, type=click.Path(), help="Cache directory")
def fetch_sources(source_type: str, output: str | None):
    """Fetch and cache source documents (RFCs, IANA, ICANN, CA/B Forum, PSL, industry, governance, DNS software)."""
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
            console.print(
                f"  [green]Fetched IANA data: {len(data.tld_list)} TLDs, "
                f"{len(data.rr_types)} RR types, {len(data.dnssec_algorithms)} DNSSEC algorithms, "
                f"{len(data.root_hints)} root servers[/green]"
            )

        if source_type in ("icann", "all"):
            from oracle.sources.icann import IcannFetcher

            icann_fetcher = IcannFetcher(cache_dir / "icann")
            sources = icann_fetcher.list_available_sources()
            console.print(f"Fetching {len(sources)} ICANN/WIPO/dispute documents...")
            for src in sources:
                await icann_fetcher.fetch_document(src["key"])
            fetched += len(sources)
            console.print(f"  [green]Fetched {len(sources)} documents[/green]")

        if source_type in ("cabforum", "all"):
            from oracle.sources.cabforum import CaBrowserForumFetcher

            cabf_fetcher = CaBrowserForumFetcher(cache_dir / "cabforum")
            docs = await cabf_fetcher.fetch_all()
            fetched += len(docs)
            console.print(f"  [green]Fetched {len(docs)} CA/Browser Forum documents[/green]")

        if source_type in ("psl", "all"):
            from oracle.sources.psl import PslFetcher

            psl_fetcher = PslFetcher(cache_dir / "psl")
            data = await psl_fetcher.fetch()
            if data:
                fetched += 1
                console.print(
                    f"  [green]Fetched PSL: {data.tld_count} TLDs, "
                    f"{data.effective_tld_count} effective TLDs, "
                    f"{data.private_suffix_count} private suffixes[/green]"
                )

        if source_type in ("industry", "all"):
            from oracle.sources.industry import IndustryFetcher

            ind_fetcher = IndustryFetcher(cache_dir / "industry")
            docs = await ind_fetcher.fetch_all()
            fetched += len(docs)
            console.print(f"  [green]Fetched {len(docs)} industry organization documents[/green]")

        if source_type in ("governance", "all"):
            from oracle.sources.governance import GovernanceFetcher

            gov_fetcher = GovernanceFetcher(cache_dir / "governance")
            docs = await gov_fetcher.fetch_all()
            fetched += len(docs)
            console.print(f"  [green]Fetched {len(docs)} governance/standards documents[/green]")

        if source_type in ("dns-software", "all"):
            from oracle.sources.dns_software import DnsSoftwareFetcher

            dns_fetcher = DnsSoftwareFetcher(cache_dir / "dns_software")
            docs = await dns_fetcher.fetch_all()
            fetched += len(docs)
            console.print(f"  [green]Fetched {len(docs)} DNS software documents[/green]")

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


# -----------------------------------------------------------------------
# retry
# -----------------------------------------------------------------------
@main.command()
@click.option("--provider", "-p", default=None, type=click.Choice(["anthropic", "openai", "ollama"]),
              help="Override provider (default: use original)")
@click.option("--model", "-m", default=None, help="Override model (default: use original)")
@click.option("--output", "-o", default=None, type=click.Path(), help="Output directory")
@click.option("--max-attempts", default=3, type=int, help="Skip failures with this many prior attempts")
@click.option("--dry-run", is_flag=True, help="Show failures without retrying")
def retry(provider: str | None, model: str | None, output: str | None, max_attempts: int, dry_run: bool):
    """Retry failed generation requests."""
    from oracle.generators.base import BaseGenerator
    from oracle.schema import ExampleFormat
    from oracle.taxonomy import get_category

    output_dir = Path(output) if output else GENERATED_DIR
    failures = BaseGenerator.load_failures(output_dir)

    if not failures:
        console.print("[green]No failures to retry.[/green]")
        return

    # Filter by max attempts
    eligible = [f for f in failures if f.attempts < max_attempts]
    skipped = len(failures) - len(eligible)

    console.print(f"\n[bold]Failures:[/bold] {len(failures)} total, {len(eligible)} eligible for retry")
    if skipped:
        console.print(f"  [dim]({skipped} skipped — reached {max_attempts} attempts)[/dim]")

    # Summary table
    table = Table(title="Failed Generations")
    table.add_column("Category", style="cyan")
    table.add_column("Subcategory")
    table.add_column("Topic")
    table.add_column("Diff")
    table.add_column("Format")
    table.add_column("Attempts", justify="right")
    table.add_column("Error", max_width=40)

    for f in eligible:
        table.add_row(
            f.category, f.subcategory, f.topic,
            f.difficulty, f.format.value,
            str(f.attempts), f.error[:40],
        )
    console.print(table)

    if dry_run:
        console.print("\n[yellow]Dry run — no retries attempted[/yellow]")
        return

    if not eligible:
        console.print("[yellow]No eligible failures to retry.[/yellow]")
        return

    async def _retry():
        from oracle.generators.synthetic import SyntheticGenerator
        from oracle.generators.tool_use import ToolUseGenerator

        succeeded = 0
        still_failed: list = []

        for f in eligible:
            cat = get_category(f.category)
            if not cat:
                console.print(f"  [red]Unknown category {f.category}, skipping[/red]")
                still_failed.append(f)
                continue

            # Find subcategory and topic in taxonomy
            sub = next((s for s in cat.subcategories if s.slug == f.subcategory), None)
            if not sub:
                console.print(f"  [red]Unknown subcategory {f.subcategory}, skipping[/red]")
                still_failed.append(f)
                continue

            topic = next((t for t in sub.topics if t.name == f.topic), None)
            if not topic:
                console.print(f"  [red]Unknown topic {f.topic}, skipping[/red]")
                still_failed.append(f)
                continue

            use_provider = provider or f.provider or "ollama"
            use_model = model or f.model or None

            console.print(
                f"  Retrying [cyan]{f.category}/{f.subcategory}/{f.topic}[/cyan] "
                f"[{f.difficulty}/{f.format.value}] (attempt {f.attempts + 1})...",
                end=" ",
            )

            try:
                if f.format == ExampleFormat.TOOL_USE:
                    gen = ToolUseGenerator(
                        output_dir=output_dir,
                        provider=use_provider,
                        model=use_model,
                    )
                    examples = await gen.generate(
                        category=cat, subcategory=sub, topic=topic,
                        difficulty=f.difficulty, count=f.count,
                    )
                else:
                    gen = SyntheticGenerator(
                        output_dir=output_dir,
                        provider=use_provider,
                        model=use_model,
                    )
                    examples = await gen.generate(
                        category=cat, subcategory=sub, topic=topic,
                        difficulty=f.difficulty, count=f.count,
                        format_type=f.format, include_thinking=f.include_thinking,
                    )

                if examples:
                    gen.save_examples(examples)
                    succeeded += len(examples)
                    console.print(f"[green]{len(examples)} examples[/green]")
                else:
                    # generate() already saved a new failure record — bump attempts
                    f.attempts += 1
                    f.error = "Retry produced 0 examples"
                    still_failed.append(f)
                    console.print("[red]0 examples[/red]")
            except Exception as e:
                f.attempts += 1
                f.error = str(e)
                still_failed.append(f)
                console.print(f"[red]error: {e}[/red]")

        # Also keep failures that exceeded max_attempts
        still_failed.extend(f for f in failures if f.attempts >= max_attempts)

        # Rewrite the failures file (replaces the append-only file with only remaining failures)
        BaseGenerator.write_failures(output_dir, still_failed)

        return succeeded, len(still_failed)

    succeeded, remaining = asyncio.run(_retry())
    console.print(f"\n[green]Retry complete: {succeeded} examples generated, {remaining} failures remaining[/green]")


if __name__ == "__main__":
    main()
