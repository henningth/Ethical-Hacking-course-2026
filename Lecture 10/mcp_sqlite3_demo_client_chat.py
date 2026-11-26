
import asyncio

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main():

    print("Connecting to HR Employee Database...")

    # Configure LLM
    model = ChatAnthropic(
        model="claude-sonnet-4-5",
        temperature=0
    )

    # Connect to MCP server
    async with MCPAdapter(SERVER_URL) as adapter:

        print("Discovering available tools...")

        tools = await asyncio.wait_for(
            adapter.list_tools(),
            timeout=15
        )

        print(f"Connected! Found {len(tools)} tools.")

        # Create agent
        agent = create_agent(
            model,
            tools,
            system_prompt="""
            You are an HR assistant with access to an employee database.

            Help HR employees retrieve information about employees,
            departments, contact details and other available records.

            Use the available database tools to answer questions.
            Do not invent employee information.
            If you cannot find the requested information, say so.

            Only retrieve information relevant to the user's question.
            """
        )

        # Conversation history
        messages = []

        print("\n" + "=" * 50)
        print("       HR EMPLOYEE DATABASE ASSISTANT")
        print("=" * 50)
        print("You can ask questions about employees and departments.")
        print("Type 'exit' to quit or 'clear' to start a new conversation.")
        print("=" * 50)

        # Interactive chat loop
        while True:

            user_input = input("\nHR Employee: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("\nGoodbye!")
                break

            if user_input.lower() == "clear":
                messages = []
                print("\nConversation history cleared.")
                continue

            # Add user message to conversation
            messages.append({
                "role": "user",
                "content": user_input
            })

            print("\nAssistant: ", end="", flush=True)

            try:
                response = await asyncio.wait_for(
                    agent.ainvoke({
                        "messages": messages
                    }),
                    timeout=60
                )

                # Update conversation history
                messages = response["messages"]

                # Display assistant response
                print(messages[-1].content)

            except asyncio.TimeoutError:
                print("\nRequest timed out.")

            except Exception as e:
                print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
