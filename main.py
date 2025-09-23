from typing import Any, Dict, List, Optional

import json
import httpx
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request


SERVER_INSTRUCTIONS = """
Zenn API と連携する Model Context Protocol (MCP) サーバです。
以下のツールを提供します:
- post_zenn_article: 新規投稿（要 write_zenn）

ChatGPT の Connectors から「Remote MCP server (SSE)」として /sse に接続してください。
"""

mcp = FastMCP('Zenn MCP', SERVER_INSTRUCTIONS)

@mcp.tool(annotations={"readOnlyHint": True})
async def post_zenn_article(
    title: str,
    body: str,
    topics: Optional[List[str]] = None,
) -> None:
    """
    Zenn に新規投稿します

    Args:
      title: 記事タイトル
      body:  本文 (Markdown)
      topics:  例: ["python", "fastmcp"]
    """
    token = get_http_request().query_params.get('token')
    if not token:
        raise ValueError("Missing 'token' query parameter. https://zenn-dev.fastmcp.app/mcp?repo_name=owner/repo&token=YOUR_TOKEN")

    repo_name = get_http_request().query_params.get('repo_name')
    if not repo_name:
        raise ValueError("Missing 'repo_name' query parameter. https://zenn-dev.fastmcp.app/mcp?repo_name=owner/repo&token=YOUR_TOKEN")

    payload: Dict[str, Any] = {
        "title": title,
        "body": body,
    }
    if topics:
        payload["topics_json"] = json.dumps(topics)
    headers = {'Authorization': 'Bearer ' + token}
    payload = {"event_type": "new_article", "client_payload": payload}
    httpx.post(f'https://api.github.com/repos/{repo_name}/dispatches', json=payload, headers=headers)

if __name__ == "__main__":
    mcp.run(transport="http")