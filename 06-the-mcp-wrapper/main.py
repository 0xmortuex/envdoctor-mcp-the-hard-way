"""Module 06: launch the server over real stdio and use it like an agent would."""

import asyncio
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import course  # noqa: E402
from mcp import ClientSession  # noqa: E402
from mcp.client.stdio import StdioServerParameters, stdio_client  # noqa: E402

SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server_mini.py")


async def session_text(root: str) -> None:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    params = StdioServerParameters(command=sys.executable, args=[SERVER, "--dir", root], env=env)
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        tools = (await session.list_tools()).tools
        assert {t.name for t in tools} == {"compare_env", "find_usage", "validate_env"}
        assert all(t.description for t in tools)

        seen = []
        res = await session.call_tool("compare_env", {})
        assert not res.is_error
        assert "Missing from .env (1): UNUSED_VAR" in res.content[0].text
        seen.append(res.content[0].text)

        res = await session.call_tool("find_usage", {})
        assert "used but undocumented: SENTRY_DSN (src/app.py:4)" in res.content[0].text
        seen.append(res.content[0].text)

        res = await session.call_tool("validate_env", {})
        assert "line 4 PORT: bad-port" in res.content[0].text
        seen.append(res.content[0].text)

        # Errors must reach the agent as instructions, not as "Error executing tool".
        res = await session.call_tool("validate_env", {"file": "../outside.env"})
        assert res.is_error and "is outside the sandbox folder" in res.content[0].text, res.content[0].text
        seen.append(res.content[0].text)
        res = await session.call_tool("compare_env", {"file": "nope.env"})
        assert res.is_error and "does not exist inside the sandbox folder" in res.content[0].text
        seen.append(res.content[0].text)

        blob = "\n".join(seen)
        for secret in course.SECRETS.values():
            assert secret not in blob, "a secret crossed the wire"
        print(f"{len(seen)} tool results, no secret on the wire")


with tempfile.TemporaryDirectory() as root:
    course.make_sample(root)
    asyncio.run(session_text(root))

# --dir must be a real folder: argparse exits with status 2 before the server starts.
import subprocess  # noqa: E402

proc = subprocess.run([sys.executable, SERVER, "--dir", os.path.join(root, "missing")], capture_output=True, text=True, timeout=60)
assert proc.returncode == 2 and "is not a directory" in proc.stderr

print("module 06 ok")
