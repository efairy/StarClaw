# -*- coding: utf-8 -*-
"""CLI commands for external agent management."""
from __future__ import annotations

import json
import sys
from typing import Optional

import click

from .http import client, print_json, resolve_base_url


def _headers(agent_id: str) -> dict:
    return {"X-Agent-Id": agent_id}


@click.group("external")
def external_group() -> None:
    """Manage and call external agents."""


# ---------------------------------------------------------------
# list
# ---------------------------------------------------------------


@external_group.command("list")
@click.option("--base-url", default=None, help="Override API base URL.")
@click.option(
    "--agent-id",
    default="default",
    help="Agent ID (defaults to 'default')",
)
@click.pass_context
def list_cmd(
    ctx: click.Context,
    base_url: Optional[str],
    agent_id: str,
) -> None:
    """List all configured external agents."""
    base_url = resolve_base_url(ctx, base_url)
    with client(base_url) as c:
        r = c.get("/external", headers=_headers(agent_id))
        r.raise_for_status()
        agents = r.json()
        if not agents:
            click.echo("No external agents configured.")
            return
        click.echo(
            f"\n  {'Key':<20s}  {'Name':<25s}  "
            f"{'Enabled':<8s}  URL"
        )
        click.echo(f"  {'─' * 80}")
        for a in agents:
            enabled = "✓" if a["enabled"] else "✗"
            url = a.get("url", "")
            if len(url) > 40:
                url = url[:37] + "..."
            click.echo(
                f"  {a['key']:<20s}  {a['name']:<25s}  "
                f"{enabled:<8s}  {url}"
            )
        click.echo()


# ---------------------------------------------------------------
# get
# ---------------------------------------------------------------


@external_group.command("get")
@click.argument("key")
@click.option("--base-url", default=None, help="Override API base URL.")
@click.option(
    "--agent-id",
    default="default",
    help="Agent ID (defaults to 'default')",
)
@click.pass_context
def get_cmd(
    ctx: click.Context,
    key: str,
    base_url: Optional[str],
    agent_id: str,
) -> None:
    """Get details of an external agent by KEY."""
    base_url = resolve_base_url(ctx, base_url)
    with client(base_url) as c:
        r = c.get(f"/external/{key}", headers=_headers(agent_id))
        if r.status_code == 404:
            raise click.ClickException(f"External agent '{key}' not found.")
        r.raise_for_status()
        print_json(r.json())


# ---------------------------------------------------------------
# add
# ---------------------------------------------------------------


@external_group.command("add")
@click.argument("key")
@click.option("--name", required=True, help="Display name.")
@click.option("--url", required=True, help="API endpoint URL.")
@click.option("--api-key", default="", help="API key for authentication.")
@click.option("--description", default="", help="Description.")
@click.option(
    "--stream/--no-stream",
    default=True,
    help="Enable streaming (default: on).",
)
@click.option(
    "--background/--no-background",
    default=False,
    help="Enable async execution (default: off).",
)
@click.option("--base-url", default=None, help="Override API base URL.")
@click.option(
    "--agent-id",
    default="default",
    help="Agent ID (defaults to 'default')",
)
@click.pass_context
def add_cmd(
    ctx: click.Context,
    key: str,
    name: str,
    url: str,
    api_key: str,
    description: str,
    stream: bool,
    background: bool,
    base_url: Optional[str],
    agent_id: str,
) -> None:
    """Add a new external agent with KEY."""
    base_url = resolve_base_url(ctx, base_url)
    payload = {
        "agent_key": key,
        "agent": {
            "name": name,
            "url": url,
            "api_key": api_key,
            "description": description,
            "stream": stream,
            "background": background,
            "enabled": True,
        },
    }
    with client(base_url) as c:
        r = c.post(
            "/external",
            json=payload,
            headers=_headers(agent_id),
        )
        if r.status_code == 400:
            raise click.ClickException(r.json().get("detail", str(r.text)))
        r.raise_for_status()
        click.echo(f"✓ External agent '{key}' created.")
        print_json(r.json())


# ---------------------------------------------------------------
# update
# ---------------------------------------------------------------


@external_group.command("update")
@click.argument("key")
@click.option("--name", default=None, help="Display name.")
@click.option("--url", default=None, help="API endpoint URL.")
@click.option("--api-key", default=None, help="API key.")
@click.option("--description", default=None, help="Description.")
@click.option(
    "--stream/--no-stream",
    default=None,
    help="Enable/disable streaming.",
)
@click.option(
    "--background/--no-background",
    default=None,
    help="Enable/disable async execution.",
)
@click.option("--base-url", default=None, help="Override API base URL.")
@click.option(
    "--agent-id",
    default="default",
    help="Agent ID (defaults to 'default')",
)
@click.pass_context
def update_cmd(
    ctx: click.Context,
    key: str,
    name: Optional[str],
    url: Optional[str],
    api_key: Optional[str],
    description: Optional[str],
    stream: Optional[bool],
    background: Optional[bool],
    base_url: Optional[str],
    agent_id: str,
) -> None:
    """Update an external agent by KEY."""
    updates = {}
    if name is not None:
        updates["name"] = name
    if url is not None:
        updates["url"] = url
    if api_key is not None:
        updates["api_key"] = api_key
    if description is not None:
        updates["description"] = description
    if stream is not None:
        updates["stream"] = stream
    if background is not None:
        updates["background"] = background

    if not updates:
        raise click.UsageError("No updates provided.")

    base_url = resolve_base_url(ctx, base_url)
    with client(base_url) as c:
        r = c.put(
            f"/external/{key}",
            json=updates,
            headers=_headers(agent_id),
        )
        if r.status_code == 404:
            raise click.ClickException(f"External agent '{key}' not found.")
        r.raise_for_status()
        click.echo(f"✓ External agent '{key}' updated.")
        print_json(r.json())


# ---------------------------------------------------------------
# delete
# ---------------------------------------------------------------


@external_group.command("delete")
@click.argument("key")
@click.option("--base-url", default=None, help="Override API base URL.")
@click.option(
    "--agent-id",
    default="default",
    help="Agent ID (defaults to 'default')",
)
@click.pass_context
def delete_cmd(
    ctx: click.Context,
    key: str,
    base_url: Optional[str],
    agent_id: str,
) -> None:
    """Delete an external agent by KEY."""
    base_url = resolve_base_url(ctx, base_url)
    with client(base_url) as c:
        r = c.delete(f"/external/{key}", headers=_headers(agent_id))
        if r.status_code == 404:
            raise click.ClickException(f"External agent '{key}' not found.")
        r.raise_for_status()
        click.echo(f"✓ External agent '{key}' deleted.")


# ---------------------------------------------------------------
# toggle
# ---------------------------------------------------------------


@external_group.command("toggle")
@click.argument("key")
@click.option("--base-url", default=None, help="Override API base URL.")
@click.option(
    "--agent-id",
    default="default",
    help="Agent ID (defaults to 'default')",
)
@click.pass_context
def toggle_cmd(
    ctx: click.Context,
    key: str,
    base_url: Optional[str],
    agent_id: str,
) -> None:
    """Toggle enabled/disabled status of an external agent."""
    base_url = resolve_base_url(ctx, base_url)
    with client(base_url) as c:
        r = c.patch(
            f"/external/{key}/toggle",
            headers=_headers(agent_id),
        )
        if r.status_code == 404:
            raise click.ClickException(f"External agent '{key}' not found.")
        r.raise_for_status()
        data = r.json()
        status = "enabled" if data["enabled"] else "disabled"
        click.echo(f"✓ External agent '{key}' is now {status}.")


# ---------------------------------------------------------------
# call
# ---------------------------------------------------------------


@external_group.command("call")
@click.argument("key")
@click.argument("text")
@click.option(
    "--stream/--no-stream",
    default=None,
    help="Override streaming setting.",
)
@click.option("--base-url", default=None, help="Override API base URL.")
@click.option(
    "--agent-id",
    default="default",
    help="Agent ID (defaults to 'default')",
)
@click.pass_context
def call_cmd(
    ctx: click.Context,
    key: str,
    text: str,
    stream: Optional[bool],
    base_url: Optional[str],
    agent_id: str,
) -> None:
    """Call an external agent with TEXT and print the response.

    Example: starclaw external call my_agent "分析一下招商证券"
    """
    import httpx as _httpx

    base_url = resolve_base_url(ctx, base_url)
    api_base = base_url.rstrip("/")
    if not api_base.endswith("/api"):
        api_base = f"{api_base}/api"

    url = f"{api_base}/external/{key}/call"
    payload = {"text": text}
    if stream is not None:
        payload["stream"] = stream

    headers = {
        "Content-Type": "application/json",
        "X-Agent-Id": agent_id,
    }

    try:
        with _httpx.Client(timeout=300.0) as http:
            with http.stream(
                "POST",
                url,
                json=payload,
                headers=headers,
            ) as resp:
                if resp.status_code == 404:
                    raise click.ClickException(
                        f"External agent '{key}' not found."
                    )
                if resp.status_code == 400:
                    resp.read()
                    detail = resp.json().get("detail", resp.text)
                    raise click.ClickException(detail)
                resp.raise_for_status()

                for line in resp.iter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                        except json.JSONDecodeError:
                            sys.stdout.write(data_str)
                            sys.stdout.flush()
                            continue

                        if data.get("done"):
                            break
                        if "error" in data:
                            click.echo(
                                click.style(
                                    f"\nError: {data['error']}",
                                    fg="red",
                                ),
                                err=True,
                            )
                            raise SystemExit(1)
                        if "text" in data:
                            sys.stdout.write(data["text"])
                            sys.stdout.flush()
        click.echo()  # Final newline
    except _httpx.TimeoutException:
        raise click.ClickException("Request timed out.")
    except _httpx.ConnectError:
        raise click.ClickException(
            f"Cannot connect to {base_url}. "
            f"Is the StarClaw server running?"
        )
