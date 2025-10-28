"# AI4J"

What is a Jira Cloud platform?
-------------------------------------
Jira Cloud platform provides a set of base functionality shared across all Jira products, such as issues, workflows, and more.

Jira products are built on top of the Jira Cloud platform. Jira Core has the same functionality as the Jira Cloud platform, whereas Jira Software and Jira Service Management have additional functionality.

You can customize, extend, and integrate with Jira by creating apps. Apps can integrate Jira with an existing service, add new features to Jira, update Jira settings, or retrieve information from Jira.

This page covers the basics of developing for Jira Cloud:

    Creating Jira apps and customizations with either Forge or Connect.
    Using the Jira APIs in apps, scripts, or one-off calls.
    Following Atlassian’s development standards for security, design, and the Atlassian Marketplace.


Documentation can be view at https://developer.atlassian.com/server/jira/platform/rest/v10007/intro/#gettingstarted



What is a large language model (LLM)?
----------------------------------------------
A large language model (LLM) is a type of artificial intelligence (AI) program that can recognize and generate text, among other tasks. LLMs are trained on huge sets of data — hence the name "large." LLMs are built on machine learning: specifically, a type of neural network called a transformer model.

In simpler terms, an LLM is a computer program that has been fed enough examples to be able to recognize and interpret human language or other types of complex data. Many LLMs are trained on data that has been gathered from the Internet — thousands or millions of gigabytes' worth of text. Some LLMs continue to crawl the web for more content after they are initially trained. But the quality of the samples impacts how well LLMs will learn natural language, so an LLM's programmers may use a more curated data set, at least at first.

LLMs use a type of machine learning called deep learning in order to understand how characters, words, and sentences function together. Deep learning involves the probabilistic analysis of unstructured data, which eventually enables the deep learning model to recognize distinctions between pieces of content without human intervention.

LLMs are then further trained via tuning: they are fine-tuned or prompt-tuned to the particular task that the programmer wants them to do, such as interpreting questions and generating responses, or translating text from one language to another.



What is Langchain?
---------------------------
LangChain is a framework for building LLM-powered applications. It helps you chain together interoperable components and third-party integrations to simplify AI application development — all while future-proofing decisions as the underlying technology evolves.

pip install langchain


LangChain is a framework for developing applications powered by large language models (LLMs).

LangChain simplifies every stage of the LLM application lifecycle:

    Development: Build your applications using LangChain's open-source components and third-party integrations. Use LangGraph to build stateful agents with first-class streaming and human-in-the-loop support.
    Productionization: Use LangSmith to inspect, monitor and evaluate your applications, so that you can continuously optimize and deploy with confidence.
    Deployment: Turn your LangGraph applications into production-ready APIs and Assistants with LangGraph Platform.

https://python.langchain.com/docs/introduction/



Why use LangChain?
-----------------------------------
LangChain helps developers build applications powered by LLMs through a standard interface for models, embeddings, vector stores, and more.

Use LangChain for:

    Real-time data augmentation. Easily connect LLMs to diverse data sources and external/internal systems, drawing from LangChain’s vast library of integrations with model providers, tools, vector stores, retrievers, and more.
    Model interoperability. Swap models in and out as your engineering team experiments to find the best choice for your application’s needs. As the industry frontier evolves, adapt quickly — LangChain’s abstractions keep you moving without losing momentum.

LangChain’s ecosystem

While the LangChain framework can be used standalone, it also integrates seamlessly with any LangChain product, giving developers a full suite of tools when building LLM applications.

To improve your LLM application development, pair LangChain with:

    LangSmith - Helpful for agent evals and observability. Debug poor-performing LLM app runs, evaluate agent trajectories, gain visibility in production, and improve performance over time.
    LangGraph - Build agents that can reliably handle complex tasks with LangGraph, our low-level agent orchestration framework. LangGraph offers customizable architecture, long-term memory, and human-in-the-loop workflows — and is trusted in production by companies like LinkedIn, Uber, Klarna, and GitLab.
    LangGraph Platform - Deploy and scale agents effortlessly with a purpose-built deployment platform for long-running, stateful workflows. Discover, reuse, configure, and share agents across teams — and iterate quickly with visual prototyping in LangGraph Studio.




What is Jira Toolkit?
-------------------------------------------------
This notebook goes over how to use the Jira toolkit.

The Jira toolkit allows agents to interact with a given Jira instance, performing actions such as searching for issues and creating issues, the tool wraps the atlassian-python-api library, for more see: https://atlassian-python-api.readthedocs.io/jira.html
Installation and setup

To use this tool, you must first set as environment variables: JIRA_INSTANCE_URL, JIRA_CLOUD

You have the choice between two authentication methods:

    API token authentication: set the JIRA_API_TOKEN (and JIRA_USERNAME if needed) environment variables
    OAuth2.0 authentication: set the JIRA_OAUTH2 environment variable as a dict having as fields "client_id" and "token" which is a dict containing at least "access_token" and "token_type"

%pip install --upgrade --quiet  atlassian-python-api

%pip install -qU langchain-community langchain-openai

import os

from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_openai import OpenAI

For authentication with API token

os.environ["JIRA_API_TOKEN"] = "abc"
os.environ["JIRA_USERNAME"] = "123"
os.environ["JIRA_INSTANCE_URL"] = "https://jira.atlassian.com"
os.environ["OPENAI_API_KEY"] = "xyz"
os.environ["JIRA_CLOUD"] = "True"

For authentication with a Oauth2.0

os.environ["JIRA_OAUTH2"] = (
    '{"client_id": "123", "token": {"access_token": "abc", "token_type": "bearer"}}'
)
os.environ["JIRA_INSTANCE_URL"] = "https://jira.atlassian.com"
os.environ["OPENAI_API_KEY"] = "xyz"
os.environ["JIRA_CLOUD"] = "True"

llm = OpenAI(temperature=0)
jira = JiraAPIWrapper()
toolkit = JiraToolkit.from_jira_api_wrapper(jira)

Tool usage

Let's see what individual tools are in the Jira toolkit:

[(tool.name, tool.description) for tool in toolkit.get_tools()]

[('JQL Query',
  '\n    This tool is a wrapper around atlassian-python-api\'s Jira jql API, useful when you need to search for Jira issues.\n    The input to this tool is a JQL query string, and will be passed into atlassian-python-api\'s Jira `jql` function,\n    For example, to find all the issues in project "Test" assigned to the me, you would pass in the following string:\n    project = Test AND assignee = currentUser()\n    or to find issues with summaries that contain the word "test", you would pass in the following string:\n    summary ~ \'test\'\n    '),
 ('Get Projects',
  "\n    This tool is a wrapper around atlassian-python-api's Jira project API, \n    useful when you need to fetch all the projects the user has access to, find out how many projects there are, or as an intermediary step that involv searching by projects. \n    there is no input to this tool.\n    "),
 ('Create Issue',
  '\n    This tool is a wrapper around atlassian-python-api\'s Jira issue_create API, useful when you need to create a Jira issue. \n    The input to this tool is a dictionary specifying the fields of the Jira issue, and will be passed into atlassian-python-api\'s Jira `issue_create` function.\n    For example, to create a low priority task called "test issue" with description "test description", you would pass in the following dictionary: \n    {{"summary": "test issue", "description": "test description", "issuetype": {{"name": "Task"}}, "priority": {{"name": "Low"}}}}\n    '),
 ('Catch all Jira API call',
  '\n    This tool is a wrapper around atlassian-python-api\'s Jira API.\n    There are other dedicated tools for fetching all projects, and creating and searching for issues, \n    use this tool if you need to perform any other actions allowed by the atlassian-python-api Jira API.\n    The input to this tool is a dictionary specifying a function from atlassian-python-api\'s Jira API, \n    as well as a list of arguments and dictionary of keyword arguments to pass into the function.\n    For example, to get all the users in a group, while increasing the max number of results to 100, you would\n    pass in the following dictionary: {{"function": "get_all_users_from_group", "args": ["group"], "kwargs": {{"limit":100}} }}\n    or to find out how many projects are in the Jira instance, you would pass in the following string:\n    {{"function": "projects"}}\n    For more information on the Jira API, refer to https://atlassian-python-api.readthedocs.io/jira.html\n    '),
 ('Create confluence page',
  'This tool is a wrapper around atlassian-python-api\'s Confluence \natlassian-python-api API, useful when you need to create a Confluence page. The input to this tool is a dictionary \nspecifying the fields of the Confluence page, and will be passed into atlassian-python-api\'s Confluence `create_page` \nfunction. For example, to create a page in the DEMO space titled "This is the title" with body "This is the body. You can use \n<strong>HTML tags</strong>!", you would pass in the following dictionary: {{"space": "DEMO", "title":"This is the \ntitle","body":"This is the body. You can use <strong>HTML tags</strong>!"}} ')]

agent = initialize_agent(
    toolkit.get_tools(), llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
)

agent.run("make a new issue in project PW to remind me to make more fried rice")



[1m> Entering new AgentExecutor chain...[0m
[32;1m[1;3m I need to create an issue in project PW
Action: Create Issue
Action Input: {"summary": "Make more fried rice", "description": "Reminder to make more fried rice", "issuetype": {"name": "Task"}, "priority": {"name": "Low"}, "project": {"key": "PW"}}[0m
Observation: [38;5;200m[1;3mNone[0m
Thought:[32;1m[1;3m I now know the final answer
Final Answer: A new issue has been created in project PW with the summary "Make more fried rice" and description "Reminder to make more fried rice".[0m

[1m> Finished chain.[0m

'A new issue has been created in project PW with the summary "Make more fried rice" and description "Reminder to make more fried rice".'

https://python.langchain.com/docs/integrations/tools/jira/
https://python.langchain.com/api_reference/community/utilities/langchain_community.utilities.jira.JiraAPIWrapper.html