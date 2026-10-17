"""
Autonomous Agent Roles implementation.
Demonstrating Planner, Researcher, Writer, and Editor specializations.
"""

from typing import List, Dict, Any, Tuple, Optional
import ast
from datetime import datetime


class PlannerAgent:
    """Decomposes complex, ill-defined research goals into an atomic, sequential plan."""

    def __init__(self, client: Any, model: str = "openai:o4-mini"):
        self.client = client
        self.model = model

    def plan(self, topic: str) -> List[str]:
        user_prompt = f"""
You are a planning agent responsible for organizing a research workflow with multiple intelligent agents.

🧠 Available agents:
- A research agent who can search the web, Wikipedia, and arXiv.
- A writer agent who can draft research summaries.
- An editor agent who can reflect and revise the drafts.

🎯 Your job is to write a clear, step-by-step research plan as a valid Python list, where each step is a string.
Each step should be atomic, executable, and must rely only on the capabilities of the above agents.

🚫 DO NOT include irrelevant tasks like "create CSV", "set up a repo", "install packages", etc.
✅ DO include real research-related tasks (e.g., search, summarize, draft, revise).
✅ DO assume tool use is available.
✅ DO NOT include explanation text — return ONLY the Python list.
✅ The final step should be to generate a Markdown document containing the complete research report.

Topic: "{topic}"
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=1.0,
        )
        steps_str = response.choices[0].message.content.strip()
        return ast.literal_eval(steps_str)


class ResearchAgent:
    """Gathers factual evidence and academic publications using external tools."""

    def __init__(self, client: Any, tools: List[Any], model: str = "openai:gpt-4o"):
        self.client = client
        self.tools = tools
        self.model = model

    def research(self, task: str, return_messages: bool = False) -> Any:
        current_time = datetime.now().strftime("%Y-%m-%d")
        prompt = f"""You are a research assistant. Current date: {current_time}.
Your task: {task}

Available tools:
- arxiv_tool: Search arXiv for academic scientific publications.
- tavily_tool: Search the web using Tavily search engine.
- wikipedia_tool: Search and read encyclopedic summaries on Wikipedia.

Conduct the necessary research using these tools and provide a detailed, accurate response.
"""
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            max_turns=6,
        )
        content = response.choices[0].message.content
        return (content, messages) if return_messages else content


class WriterAgent:
    """Synthesizes structured research findings into a coherent draft."""

    def __init__(self, client: Any, model: str = "openai:gpt-4o"):
        self.client = client
        self.model = model

    def write(self, task: str) -> str:
        system_prompt = "You are a writing agent specialized in generating well-structured academic or technical content."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=1.0,
        )
        return response.choices[0].message.content


class EditorAgent:
    """Performs critical reflection, structural critique, and revision."""

    def __init__(self, client: Any, model: str = "openai:gpt-4o"):
        self.client = client
        self.model = model

    def edit(self, task: str) -> str:
        system_prompt = "You are an editor agent specialized in reflecting on, critiquing, or improving existing drafts."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
