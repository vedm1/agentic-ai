from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os
from crewai_tools import SerperDevTool


@CrewBase
class MyFinancialResearcher():
    """MyFinancialResearcher crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        super().__init__()
        # Configure LLM with max_tokens to prevent cutoff
        self.llm = LLM(
            model=os.getenv("MODEL", "claude-sonnet-4-5")
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            tools=[SerperDevTool()],
            llm=self.llm
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst'],
            verbose=True,
            max_iter=50,
            llm=self.llm
        )

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config['research_task'])

    @task
    def analysis_part1_task(self) -> Task:
        return Task(config=self.tasks_config['analysis_part1_task'])

    @task
    def analysis_part2_task(self) -> Task:
        return Task(config=self.tasks_config['analysis_part2_task'])

    @task
    def analysis_part3_task(self) -> Task:
        return Task(config=self.tasks_config['analysis_part3_task'])

    @task
    def combine_report_task(self) -> Task:
        return Task(config=self.tasks_config['combine_report_task'])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
