import asyncio
import json
import os
import sys
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from hyperbrowser import AsyncHyperbrowser
from hyperbrowser.models.extract import StartExtractJobParams
from hyperbrowser.models.session import CreateSessionParams, CreateSessionProfile

from config import settings
from schemas import AllFollowers, AllTweets

client = AsyncHyperbrowser(
    api_key=settings.HYPERBROWSER_API_KEY,
)

console = Console()


async def create_session_params(
    initial_session_creation: bool = False,
) -> CreateSessionParams:
    """
    Creates a new session profile if one is not specified in the config.

    Returns:
        CreateSessionParams: The create session params.
    """
    profile_id = settings.PROFILE_ID
    if not profile_id:
        profile = await client.profiles.create()
        profile_id = profile.id
        with open(".profile", "w") as f:
            f.write(f"\nPROFILE_ID={profile_id}")
    print("Using profile id ", profile_id)

    return CreateSessionParams(
        use_stealth=True,
        use_proxy=True,
        adblock=True,
        annoyances=True,
        accept_cookies=True,
        proxy_server=settings.PROXY_SERVER_URL,
        proxy_server_username=settings.PROXY_SERVER_USERNAME,
        proxy_server_password=settings.PROXY_SERVER_PASSWORD,
        profile=CreateSessionProfile(
            id=profile_id, persist_changes=initial_session_creation
        ),
    )


async def create_session():
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Creating session..."),
        transient=True,
    ) as progress:
        progress.add_task("create", total=None)
        session_params = await create_session_params(True)
        session = await client.sessions.create(params=session_params)

    if (not session) or (not session_params.profile):
        console.print("[bold red]Failed to create session[/]")
        raise Exception("Failed to create session")

    # Store session ID in a file
    with open(".session", "w") as f:
        json.dump({"session_id": session.id}, f)

    console.print(f"[bold green]Created session with ID:[/] {session.id}")
    console.print(f"[bold green]Using profile ID:[/] {session_params.profile.id}")
    console.print(f"[bold green]Session is live at:[/]")
    print(session.live_url)
    console.print(
        f"[bold yellow]Close the session when done with it {" ".join(sys.orig_argv[:-1])} stop --session-id {session.id}[/]"
    )
    return session


async def extract_tweets_with_profile(handle: str):
    console.print(f"[bold]Extracting tweets for @{handle}...[/]")

    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold green]Fetching tweets from @{handle}..."),
        transient=True,
    ) as progress:
        progress.add_task("extract", total=None)
        session_params = await create_session_params()
        result = await client.extract.start_and_wait(
            StartExtractJobParams(
                urls=[f"https://twitter.com/{handle}"],
                prompt=f"Extract the 10 most recent tweets from this @{handle}. The following is @{handle}'s twitter profile in Markdown format:",
                schema=AllTweets,
                session_options=session_params,
            )
        )

    console.print(f"[bold green]Successfully extracted tweets for @{handle}[/]")

    with open(f"{handle}_tweets.json", "w+") as f:
        json.dump(result.data, f, indent=2)

    console.print(f"[bold]Saved tweets to[/] {handle}_tweets.json")
    return result


async def extract_followers(handle: str):
    console.print(f"[bold]Extracting followers for @{handle}...[/]")

    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold green]Fetching followers from @{handle}..."),
        transient=True,
    ) as progress:
        progress.add_task("extract", total=None)
        session_params = await create_session_params()
        result = await client.extract.start_and_wait(
            StartExtractJobParams(
                urls=[f"https://twitter.com/{handle}/verified_followers"],
                prompt=f"Extract all the followers of @{handle} from this page. The following is @{handle}'s twitter verified followers page in Markdown format:",
                schema=AllFollowers,
                session_options=session_params,
                wait_for=25,
            )
        )

    console.print(f"[bold green]Successfully extracted followers for @{handle}[/]")

    with open(f"{handle}_followers.json", "w+") as f:
        json.dump(result.data, f, indent=2)

    console.print(f"[bold]Saved followers to[/] {handle}_followers.json")
    return result


async def stop_session(session_id: str | None = None):
    """Stop a browser session."""
    if not session_id:
        try:
            with open(".session", "r") as f:
                data = json.load(f)
                session_id = data.get("session_id")
        except FileNotFoundError:
            console.print("[bold red]No active session found[/]")
            return

    if not session_id:
        console.print("[bold red]No session ID provided or found[/]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Stopping session..."),
        transient=True,
    ) as progress:
        progress.add_task("stop", total=None)
        await client.sessions.stop(session_id)

    console.print(f"[bold green]Successfully stopped session:[/] {session_id}")

    # Remove the session file if it exists
    try:
        import os

        os.remove(".session")
    except FileNotFoundError:
        pass


@click.group()
def cli():
    """Twitter data extraction tool using Hyperbrowser."""
    pass


@cli.command("session")
def session_command():
    """Create a new browser session. Use this to create a new session profile if one is not specified in the config."""
    asyncio.run(create_session())


@cli.command("tweets")
@click.argument("handle")
def tweets_command(handle):
    """Extract tweets from a Twitter profile."""
    asyncio.run(extract_tweets_with_profile(handle))


@cli.command("followers")
@click.argument("handle")
def followers_command(handle):
    """Extract followers from a Twitter profile."""
    asyncio.run(extract_followers(handle))


@cli.command("all")
@click.argument("handle")
def all_command(handle):
    """Extract both tweets and followers from a Twitter profile."""

    async def run_all():
        await extract_tweets_with_profile(handle)
        await asyncio.sleep(2)
        await extract_followers(handle)

    asyncio.run(run_all())


@cli.command("stop")
@click.option(
    "--session-id",
    help="Session ID to stop. If not provided, will use the last created session.",
)
def stop_session_command(session_id: str | None):
    """Stop a browser session."""
    asyncio.run(stop_session(session_id))


if __name__ == "__main__":
    cli()
