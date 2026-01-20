"""
Sidekick Personal Co-worker - A LangGraph agent with Playwright browser tools
Run with: python sidekick.py
"""

import uuid
import asyncio
from typing import Annotated, Optional, Dict, List, Any

from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import TypedDict
import gradio as gr

# Load environment variables
load_dotenv(override=True)


# ============== Models ==============

class EvaluatorOutput(BaseModel):
    feedback: str = Field(description="Feedback on the worker's response")
    success_criteria_met: bool = Field(description="True if success criteria have been met")
    user_input_needed: bool = Field(description="True if more input is needed from the user")


class State(TypedDict):
    messages: Annotated[List[Any], add_messages]
    success_criteria: str
    feedback_on_work: Optional[str]
    success_criteria_met: bool
    user_input_needed: bool


# ============== Browser & Tools Setup ==============

async_browser = None
tools = []


async def setup_browser():
    """Initialize the async Playwright browser."""
    global async_browser, tools
    print("Starting Playwright browser...")
    async_browser = await create_async_playwright_browser(headless=False)
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
    tools = toolkit.get_tools()
    print(f"Loaded {len(tools)} browser tools")


# ============== LLMs ==============

worker_llm = ChatOpenAI(model="gpt-4o-mini")
evaluator_llm = ChatOpenAI(model="gpt-4o-mini")
evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)


# ============== Node Functions ==============

def worker(state: State) -> Dict[str, Any]:
    """Worker node that uses tools to complete tasks."""
    system_message = f"""You are a helpful assistant that can use tools to complete tasks.
You keep working on a task until either you have a question or clarification for the user, or the success criteria is met.
This is the success criteria:
{state['success_criteria']}
You should reply either with a question for the user about this assignment, or with your final response.
If you have a question for the user, you need to reply by clearly stating your question. An example might be:

Question: please clarify whether you want a summary or a detailed answer

If you've finished, reply with the final answer, and don't ask a question; simply reply with the answer.
"""

    if state.get('feedback_on_work'):
        system_message += f"""
Previously you thought you completed the assignment, but your reply was rejected because the success criteria was not met.
Here is the feedback on why this was rejected:
{state['feedback_on_work']}
With this feedback, please continue the assignment, ensuring that you meet the success criteria or have a question for the user."""

    found_system_message = False
    messages = list(state["messages"])
    for msg in messages:
        if isinstance(msg, SystemMessage):
            msg.content = system_message
            found_system_message = True

    if not found_system_message:
        messages = [SystemMessage(content=system_message)] + messages

    # Bind tools dynamically (tools are set up after browser initialization)
    llm_with_tools = worker_llm.bind_tools(tools)
    response = llm_with_tools.invoke(messages)
    print(f"[Worker] Done - tool_calls: {bool(response.tool_calls)}")

    return {"messages": [response]}


def worker_router(state: State) -> str:
    """Route to tools or evaluator based on whether tool calls are present."""
    last_message = state["messages"][-1]
    route = "tools" if hasattr(last_message, "tool_calls") and last_message.tool_calls else "evaluator"
    print(f"[Router] -> {route}")
    return route


def format_conversation(messages: List[Any]) -> str:
    """Format conversation history for the evaluator."""
    conversation = "Conversation history:\n\n"
    for message in messages:
        if isinstance(message, HumanMessage):
            conversation += f"User: {message.content}\n"
        elif isinstance(message, AIMessage):
            text = message.content or "[Tools use]"
            conversation += f"Assistant: {text}\n"
    return conversation


def evaluator(state: State) -> Dict[str, Any]:
    """Evaluator node that checks if success criteria are met."""
    last_response = state["messages"][-1].content

    system_message = """You are an evaluator that determines if a task has been completed successfully by an Assistant.
Assess the Assistant's last response based on the given criteria. Respond with your feedback, and with your decision on whether the success criteria has been met,
and whether more input is needed from the user."""

    user_message = f"""You are evaluating a conversation between the User and Assistant. You decide what action to take based on the last response from the Assistant.

The entire conversation with the assistant, with the user's original request and all replies, is:
{format_conversation(state['messages'])}

The success criteria for this assignment is:
{state['success_criteria']}

And the final response from the Assistant that you are evaluating is:
{last_response}

Respond with your feedback, and decide if the success criteria is met by this response.
Also, decide if more user input is required, either because the assistant has a question, needs clarification, or seems to be stuck and unable to answer without help.
"""
    if state.get("feedback_on_work"):
        user_message += f"Also, note that in a prior attempt from the Assistant, you provided this feedback: {state['feedback_on_work']}\n"
        user_message += "If you're seeing the Assistant repeating the same mistakes, then consider responding that user input is required."

    evaluator_messages = [SystemMessage(content=system_message), HumanMessage(content=user_message)]

    eval_result = evaluator_llm_with_output.invoke(evaluator_messages)
    print(f"[Evaluator] Done - met: {eval_result.success_criteria_met}, user_input: {eval_result.user_input_needed}")

    return {
        "messages": [{"role": "assistant", "content": f"Evaluator Feedback: {eval_result.feedback}"}],
        "feedback_on_work": eval_result.feedback,
        "success_criteria_met": eval_result.success_criteria_met,
        "user_input_needed": eval_result.user_input_needed
    }


def route_based_on_evaluation(state: State) -> str:
    """Route based on evaluation results."""
    result = "END" if state["success_criteria_met"] or state["user_input_needed"] else "worker"
    print(f"[Eval Router] -> {result}")
    return result


async def tool_executor(state: State) -> Dict[str, Any]:
    """Execute tools asynchronously."""
    print("[Tools] Started")
    messages = state["messages"]
    last_message = messages[-1]

    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        print("[Tools] No tool calls found")
        return {"messages": []}

    tool_results = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        print(f"[Tools] Executing: {tool_name}")

        tool = next((t for t in tools if t.name == tool_name), None)
        if tool is None:
            print(f"[Tools] Tool not found: {tool_name}")
            continue

        try:
            result = await tool.ainvoke(tool_args)
            print(f"[Tools] Success: {str(result)[:100]}...")
            tool_results.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call['id']
            ))
        except Exception as e:
            print(f"[Tools] Error: {e}")
            tool_results.append(ToolMessage(
                content=f"Error: {e}",
                tool_call_id=tool_call['id']
            ))

    print("[Tools] Done")
    return {"messages": tool_results}


# ============== Build Graph ==============

graph_builder = StateGraph(State)

graph_builder.add_node("worker", worker)
graph_builder.add_node("evaluator", evaluator)
graph_builder.add_node("tools", tool_executor)

graph_builder.add_conditional_edges("worker", worker_router, {"tools": "tools", "evaluator": "evaluator"})
graph_builder.add_edge("tools", "worker")
graph_builder.add_conditional_edges("evaluator", route_based_on_evaluation, {"worker": "worker", "END": END})
graph_builder.add_edge(START, "worker")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

print("Graph compiled successfully")


# ============== Gradio Interface ==============

def make_thread_id() -> str:
    return str(uuid.uuid4())


async def process_message(message, success_criteria, history, thread):
    """Process a user message through the graph."""
    config = {"configurable": {"thread_id": thread}}

    state = {
        "messages": [{"role": "user", "content": message}],
        "success_criteria": success_criteria,
        "feedback_on_work": None,
        "user_input_needed": False,
        "success_criteria_met": False
    }

    result = await graph.ainvoke(state, config=config)

    user = {"role": "user", "content": message}
    reply = {"role": "assistant", "content": result["messages"][-2].content}
    feedback = {"role": "assistant", "content": result["messages"][-1].content}
    return history + [user, reply, feedback]


def reset():
    return "", "", None, make_thread_id()


# ============== Main ==============

if __name__ == "__main__":
    with gr.Blocks() as demo:
        gr.Markdown("## Sidekick Personal Co-worker")
        thread = gr.State(make_thread_id())

        with gr.Row():
            chatbot = gr.Chatbot(label="Sidekick Personal Co-worker", height=300, type="messages")
        with gr.Group():
            with gr.Row():
                message = gr.Textbox(show_label=False, placeholder="Your request to your sidekick")
            with gr.Row():
                success_criteria = gr.Textbox(show_label=False, placeholder="What are your success criteria?")
        with gr.Row():
            reset_button = gr.Button("Reset", variant="stop")
            go_button = gr.Button("Go!", variant="primary")

        message.submit(process_message, [message, success_criteria, chatbot, thread], [chatbot])
        success_criteria.submit(process_message, [message, success_criteria, chatbot, thread], [chatbot])
        go_button.click(process_message, [message, success_criteria, chatbot, thread], [chatbot])
        reset_button.click(reset, [], [message, success_criteria, chatbot, thread])

    print("\nStarting Gradio server...")
    demo.launch()