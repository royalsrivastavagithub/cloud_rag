# controllers/agent_controller.py

from inspect import signature, Parameter
from typing import Any

from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Import your backend functions
from controllers.log_controller import pull_and_save_logs
from controllers.rag_controller import (
    query_logs,
    summary_logs,
    health_report,
    get_error_logs
)

# ---------------------------
# 1. Define tools
# ---------------------------
tools = [
    Tool(
        name="pull_logs",
        func=pull_and_save_logs,
        description="Fetch latest logs from AWS CloudWatch."
    ),
    Tool(
        name="query_logs",
        func=query_logs,
        description="Search logs using semantic RAG."
    ),
    Tool(
        name="summarize_logs",
        func=summary_logs,
        description="Summarize log chunks into readable text."
    ),
    Tool(
        name="get_error_logs",
        func=get_error_logs,
        description="Return only error logs."
    ),
    Tool(
        name="health_report",
        func=health_report,
        description="Generate a system health status report."
    )
]

# Quick lookup map
TOOL_MAP = {t.name: t.func for t in tools}

# ---------------------------
# 2. LLM
# ---------------------------
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# ---------------------------
# 3. Prompt
# ---------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an intelligent log analysis agent. "
     "Use the available tools to inspect logs, detect issues, "
     "and produce root-cause explanations. "
     "Call tools whenever needed. Respond clearly."),
    ("human", "{input}")
])

# Create LCEL chain
chain = prompt | llm.bind_tools(tools)


# ---------------------------
# Helper: call a tool safely
# ---------------------------
def call_tool_safely(tool_func, args_dict: dict) -> Any:
    """
    Call the provided tool_func with args_dict from the model.
    Handles:
      - tools that accept 0 args
      - tools that accept positional or keyword args
      - model-provided args where keys are like '__arg1'
    Returns the tool result (or an error string on exception).
    """
    try:
        sig = signature(tool_func)
        # count only positional-or-keyword parameters (ignore VAR_POSITIONAL/VAR_KEYWORD)
        param_count = sum(
            1 for p in sig.parameters.values()
            if p.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
        )

        # No parameters expected: ignore any args sent by the model
        if param_count == 0:
            return tool_func()

        # Try calling with keyword args first (if the arg names match)
        if args_dict:
            try:
                # We try to call with the raw args dict — if args are named properly this will succeed.
                return tool_func(**args_dict)
            except TypeError:
                # If keyword calling fails, try positional by order of values
                try:
                    return tool_func(*list(args_dict.values()))
                except TypeError:
                    # Last resort: try converting special __arg1 keys to positional values
                    vals = [v for k, v in sorted(args_dict.items())]
                    return tool_func(*vals)

        # If no args were provided but tool expects some, call without args (best-effort)
        return tool_func()

    except Exception as e:
        # Return readable error to feed back to the model
        return f"TOOL_ERROR: {type(e).__name__}: {e}"


# ---------------------------
# 4. Full Agent Execution Loop
# ---------------------------
def run_agent(user_query: str):
    """
    Executes full agent loop:
    - Send user query to LLM
    - Detect tool calls
    - Execute tools (safely)
    - Feed tool output back to LLM
    - Return final answer
    """
    # initial input for the chain
    next_input = user_query
    # keep a simple conversation list if you want (not strictly needed here)
    # we use the chain.invoke loop pattern: pass {"input": next_input}
    while True:
        ai_msg = chain.invoke({"input": next_input})

        # If LLM made tool calls, execute them and feed results back
        tool_calls = getattr(ai_msg, "tool_calls", None) or []
        if tool_calls:
            # append the assistant message (which may be empty) then each tool result
            # we will build a combined textual "tool outputs" string to pass back in next_input
            tool_outputs = []
            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args", {})

                tool_func = TOOL_MAP.get(tool_name)
                if tool_func is None:
                    tool_result = f"TOOL_ERROR: unknown tool {tool_name}"
                else:
                    tool_result = call_tool_safely(tool_func, tool_args)

                # Normalize tool_result to string for the LLM
                if not isinstance(tool_result, str):
                    try:
                        tool_result_str = str(tool_result)
                    except Exception:
                        tool_result_str = repr(tool_result)
                else:
                    tool_result_str = tool_result

                # Save the output with identifier so the model can reference it
                out_block = (
                    f"[tool_output name={tool_name} id={tool_call.get('id','')}]\n"
                    f"{tool_result_str}\n"
                    f"[/tool_output]\n"
                )
                tool_outputs.append(out_block)

            # Feed combined tool outputs back to the chain by making them the next input
            # We include the original assistant content (if any) + tool outputs so the model sees context.
            assistant_content = ai_msg.content or ""
            next_input = assistant_content + "\n\n" + "\n".join(tool_outputs)
            # continue loop so LLM can process tool results and produce final answer
            continue

        # No tool calls -> final answer available
        return ai_msg.content
