
import asyncio

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main():

    print("1. Configuring LLM...")

    model = ChatAnthropic(
        model="claude-sonnet-4-5",
        temperature=0
    )

    print("2. Connecting to MCP server...")

    async with MCPAdapter(SERVER_URL) as adapter:

        print("3. Discovering tools...")

        tools = await asyncio.wait_for(
            adapter.list_tools(),
            timeout=15
        )

        print(f"   Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}")

        print("4. Creating agent...")

        agent = create_agent(model, tools)

        print("5. Invoking agent...")

        response = await asyncio.wait_for(
            agent.ainvoke({
                "messages": [
                    {
                        "role": "user",
                        "content": "Say hello to Alice."
                    }
                ]
            }),
            timeout=60
        )

        print("6. Agent response:")
        print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
