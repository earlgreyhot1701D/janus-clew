"""Janus Clew CLI - Main entry point with comprehensive error handling."""

import sys
from pathlib import Path
from typing import List

import click

from config import ERROR_MESSAGES, SUCCESS_MESSAGES, VERBOSE, DEBUG
from logger import get_logger
from exceptions import JanusException, NoRepositoriesError
from cli.analyzer import AnalysisEngine
from cli.storage import StorageManager

logger = get_logger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool):
    """🧵 Janus Clew - Evidence-backed growth tracking."""
    if verbose:
        logger.setLevel("DEBUG")
        logger.debug("Verbose mode enabled")
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.argument("repos", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--force", "-f", is_flag=True, help="Force re-analysis (ignore cache)")
@click.pass_context
def analyze(ctx: click.Context, repos: tuple, force: bool):
    """Analyze repositories and track your growth.

    Example:
        janus-clew analyze ~/Your-Honor ~/Ariadne-Clew ~/TicketGlass
    """
    try:
        if not repos:
            raise NoRepositoriesError()

        click.secho(SUCCESS_MESSAGES["analysis_start"], fg="cyan", bold=True)
        click.echo()

        # Step 1: Analyze repositories
        click.secho("📊 Step 1: Analyzing repositories...", fg="blue", bold=True)
        try:
            analysis_engine = AnalysisEngine()
            analysis = analysis_engine.run(list(repos))
            logger.info(f"Analysis complete: {len(analysis['projects'])} projects analyzed")

            # Display analysis progress
            for project in analysis["projects"]:
                tech_str = ", ".join(project["technologies"][:2])
                if len(project["technologies"]) > 2:
                    tech_str += f", +{len(project['technologies']) - 2} more"

                click.echo(f"   ✓ {project['name']}: {project['complexity_score']:.1f} complexity | {tech_str}")

        except JanusException as e:
            click.echo(f"{e}", err=True)
            logger.error(f"Analysis error: {e.code} - {e.message}", extra={"repos": list(repos)})
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Unexpected error during analysis: {e}", err=True)
            logger.error(f"Unexpected analysis error: {type(e).__name__}: {e}", exc_info=True, extra={"repos": list(repos)})
            sys.exit(1)

        # Step 2: Save results
        click.secho("💾 Step 2: Saving analysis...", fg="blue", bold=True)
        try:
            storage = StorageManager()
            filepath = storage.save_analysis(analysis)
            click.echo(SUCCESS_MESSAGES["data_saved"].format(path=filepath))
        except JanusException as e:
            click.echo(f"{e}", err=True)
            logger.error(f"Storage error: {e.code} - {e.message}")
            sys.exit(1)

        # Step 3: Display results
        click.secho()
        click.secho("📈 Your Growth Journey", fg="green", bold=True)
        click.secho("=" * 60, fg="green")

        for i, project in enumerate(analysis["projects"], 1):
            tech_str = ", ".join(project["technologies"][:3])
            if len(project["technologies"]) > 3:
                tech_str += f", +{len(project['technologies']) - 3} more"

            click.echo()
            click.echo(f"{i}. {project['name']}")
            click.echo(f"   Complexity: {project['complexity_score']:.1f}/10")
            click.echo(f"   Commits: {project['commits']}")
            click.echo(f"   Technologies: {tech_str}")

        click.echo()
        click.echo("=" * 60)
        avg = analysis["overall"]["avg_complexity"]
        growth = analysis["overall"]["growth_rate"]
        click.echo(f"Average Complexity: {avg:.1f}/10")
        click.echo(f"Growth Rate: {growth:+.1f}%")

        # Display errors if any
        if analysis.get("errors"):
            click.echo()
            click.echo(f"⚠️  {len(analysis['errors'])} repositories failed:")
            for error in analysis["errors"]:
                click.echo(f"   - {error['repo']}: {error['error']}")

        click.secho()
        click.secho(SUCCESS_MESSAGES["analysis_complete"], fg="green", bold=True)
        click.secho()
        click.echo("Next: Start the dashboard")
        click.echo("  python -m backend.server")

    except NoRepositoriesError as e:
        click.echo(f"{e}", err=True)
        logger.error(f"CLI error: {e.code} - {e.message}", extra={"repos": repos})
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        logger.error(f"Fatal CLI error: {type(e).__name__}: {e}", exc_info=True, extra={"repos": repos})
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx: click.Context):
    """Show status of stored analyses."""
    try:
        storage = StorageManager()
        count = storage.get_analysis_count()

        click.echo("📊 Janus Clew - Analysis Status")
        click.echo(f"Total analyses stored: {count}")

        if count > 0:
            latest = storage.load_latest_analysis()
            if latest:
                click.echo()
                click.echo("Latest analysis:")
                for project in latest.get("projects", []):
                    click.echo(f"  - {project['name']}: {project['complexity_score']:.1f} complexity")
        else:
            click.echo()
            click.echo("No analyses found. Run: janus-clew analyze <repos>")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        logger.error(f"Status command error: {type(e).__name__}: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def demo(ctx: click.Context):
    """Run demo analysis with sample repositories."""
    try:
        click.echo("🧵 Janus Clew Demo")
        click.echo("=" * 60)
        click.echo()
        click.echo("This is a demo showing how Janus Clew works.")
        click.echo()
        click.echo("Demo repositories should be at:")
        click.echo("  - ~/Your-Honor")
        click.echo("  - ~/Ariadne-Clew")
        click.echo("  - ~/TicketGlass")
        click.echo()
        click.echo("To run demo: janus-clew analyze ~/Your-Honor ~/Ariadne-Clew ~/TicketGlass")
        click.echo()

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for CLI."""
    try:
        cli(obj={})
    except click.exceptions.Abort:
        sys.exit(130)  # SIGINT
    except click.exceptions.Exit as e:
        sys.exit(e.exit_code)
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        click.echo(f"❌ Unhandled error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
