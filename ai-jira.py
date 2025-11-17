from fastapi import FastAPI
import uvicorn

from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain.tools import tool
import os
import pandas as pd

from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_ollama import OllamaLLM
from typing import Union

new_api_token = "ATATT3xFfGF0XOcO8T_XvfXS3GIvkH_AKaAnwWjUAYVCvUe123Ygro0xOhkHx_hT1_KZQXQUAgaw77q8K5S3ZRXpSn8qdBFww3F4dK7NDYndi4t7UqAu8qmWx9vxoTZcwHUCnOvwX4D3qnsfFJwaWdpqYhOXT3WMQn90h2Z5BQgfzpOr4eUP_8c=B53A6888"
JIRA_INSTANCE_URL = "https://sadegh-beasy4biz.atlassian.net"
JIRA_URL = "https://sadegh-beasy4biz.atlassian.net"
USERNAME = "sadegh.astaneh@beasy4biz.com"
API_TOKEN = "ATATT3xFfGF0XOcO8T_XvfXS3GIvkH_AKaAnwWjUAYVCvUe123Ygro0xOhkHx_hT1_KZQXQUAgaw77q8K5S3ZRXpSn8qdBFww3F4dK7NDYndi4t7UqAu8qmWx9vxoTZcwHUCnOvwX4D3qnsfFJwaWdpqYhOXT3WMQn90h2Z5BQgfzpOr4eUP_8c=B53A6888"
JIRA_USERNAME = "sadegh.astaneh@beasy4biz.com"
JIRA_API_TOKEN = "ATATT3xFfGF0XOcO8T_XvfXS3GIvkH_AKaAnwWjUAYVCvUe123Ygro0xOhkHx_hT1_KZQXQUAgaw77q8K5S3ZRXpSn8qdBFww3F4dK7NDYndi4t7UqAu8qmWx9vxoTZcwHUCnOvwX4D3qnsfFJwaWdpqYhOXT3WMQn90h2Z5BQgfzpOr4eUP_8c=B53A6888"

from langchain_core.messages import HumanMessage


from atlassian import Jira
import requests
from langchain_text_splitters import RecursiveJsonSplitter
from langchain.schema import Document
import pandas as pd
import json
import base64

def find_related_tickets(primary_issue_key, primary_issue_data, issues):
    args = [(key, data, primary_issue_key, primary_issue_data) for key, data in issues.items()]
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count()) as executor:
        executor.map(check_issue_and_link_helper, args)
        

def parse_jira_issue_fields(data: dict) -> tuple:
    """Extract the key, summary and description fields from Jira.
    Args:
        data: Jira response JSON object.
    Returns:
        The Jira key, also concatenates the summary and description fields.
    """
    key = data.get('key')
    summary_description = f"{data.get('fields',{}).get('summary')} {data.get('fields',{}).get('description')}" 
    return (key, summary_description)

def get_all_fields() -> Union[dict, None]:
    cf = ["Assegnatario","Progetto","Tipo Ticket","ID Ticket","STS","Titolo Ticket","Priorità","Stato","Note"]
    try:
        result = requests.get(f'{JIRA_INSTANCE_URL}/rest/api/3/field', auth=(JIRA_USERNAME, JIRA_API_TOKEN))
        fields = result.json()
        field = {}
        for el in fields:
            if el["custom"] and el["name"] in cf:
                field[el["name"]] = el["id"]
        return field
    except Exception as e:
        print(f'ERROR get_all_fields: {e}')

columns=['ID Ticket', 'Titolo Ticket','Tipo Ticket','Progetto','Note','Priorità','Stato','Assegnatario','STS']

field = get_all_fields()
print(field)

def get_all_tickets() -> Union[dict, None]:
    """Get all unresolved Jira tickets for a Jira project (maximum 1000). 
    Args:
        
    Returns:
        A dictionary of Jira key, description and summary data.
    """
    try:
        if (result := requests.get(f'{JIRA_INSTANCE_URL}/rest/api/2/search?jql=project={PROJECT_KEY}+AND+resolution=unresolved&maxResults=1000', auth=(JIRA_USERNAME, JIRA_API_TOKEN))) \
        and (issues := result.json().get('issues')):
            return {parse_jira_issue_fields(issue)[0]: parse_jira_issue_fields(issue)[1] for issue in issues}
    except Exception as e:
        print(f'ERROR get_all_tickets: {e}')

def get_ticket_data(key: str) -> Union[dict, None]:
    """Get Jira issue data. 
    Args:
        key: Jira issue key to be looked up.
    Returns:
        Jira ticket data.
    """
    try:
        if (result := requests.get(f'{JIRA_INSTANCE_URL}/rest/agile/1.0/issue/{key}', auth=(JIRA_USERNAME, JIRA_API_TOKEN))):
            return parse_jira_issue_fields(result.json())
    except Exception as e:
        print(f'ERROR get_ticket_data: {e}')


@tool
def triage(ticket_number:str) -> str:
    """triage a given ticket and link related tickets"""
    ticket_number = str(ticket_number)
    all_tickets = get_all_tickets()
    primary_issue_key, primary_issue_data = get_ticket_data(ticket_number)
    find_related_tickets(primary_issue_key, primary_issue_data, all_tickets)
    user_stories_acceptance_criteria_priority(primary_issue_key, primary_issue_data)
    return "Task complete"

session = requests.Session()
jira = Jira(
    url=JIRA_URL,
    username=USERNAME,
    password=API_TOKEN,
    cloud=True,  # Ensure this is set to True for Jira Cloud
    session=session  # Optional: use a session for persistent connections
)


#board = jira.get_all_agile_boards(board_name=None, project_key=None, board_type=None, start=0, limit=50)
#print(json.dumps(board, indent=4))

os.environ["OLLAMA_MODELS"]="/ollama"
os.environ["JIRA_API_TOKEN"] = API_TOKEN
os.environ["JIRA_USERNAME"] = USERNAME
os.environ["JIRA_INSTANCE_URL"] = JIRA_URL
os.environ["OPENAI_API_KEY"] = "xyz"
os.environ["JIRA_CLOUD"] = "True"

llm = OllamaLLM(model="qwen2.5vl:7b", base_url="http://ollama:11434")

jira = JiraAPIWrapper()

toolkit = JiraToolkit.from_jira_api_wrapper(jira)
agent = initialize_agent(
    toolkit.get_tools() + [triage],
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True,
    early_stopping_method="force", 
    max_iterations=1,
    return_intermediate_steps=True
)



# Load environment variables from .env file
load_dotenv()


PROJECT_KEY = "SUPPORT"
# local imports
EXAMPLE_PROMPTS = [
    f"Can you show me in details all Jira issues of {PROJECT_KEY} in list format??",
    f"Can you show me in details all Jira issues of {PROJECT_KEY} in json format?",
    f"How many issues are in status 'AM2' in project {PROJECT_KEY} and show them in details in list format?",
    f"Create a new task in project {PROJECT_KEY} with description 'This is a test'.",
    f"What are the issues that are in status 'IN PROGRESS' in project {PROJECT_KEY} show them in details in list format?",
    f"Transition the tasks that are in status 'To Do' in project {PROJECT_KEY} to 'IN PROGRESS'",
    f"Transition the tasks that are in status 'IN PROGRESS' in project {PROJECT_KEY} to 'DONE'",
    "Quanti problemi sono nello stato 'AM2' nel progetto SUPPORT",
    "Quanti ticket sono nello stato 'AM2' e priorità 'alta'   nel progetto SUPPORT"
]

            
def get_jira_issues(query, max_results=50):
    jira_api_url = f"{JIRA_URL}/rest/api/3/search/jql"
    base64_credentials = base64.b64encode(
        f"{USERNAME}:{API_TOKEN}".encode()
    ).decode()
    headers = {
        "Authorization": f"Basic {base64_credentials}",
        "Content-Type": "application/json",
    }
    issues = []
    next_page_token = None

    while True:
        params = {
        "jql": query,
        "fields": '*all',
        "maxResults": max_results,
        }
        if next_page_token:
            params["nextPageToken"] = next_page_token
        response = requests.get(jira_api_url, headers=headers, params=params)
        print("XXXX ", response, response.json())
        if response.status_code == 200:
            data = response.json()
            issues.extend(data.get("issues", []))
            next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break
    df = pd.DataFrame(columns=columns)
    for issue in issues:
        key = issue["fields"][field["ID Ticket"]]
        progetto = ""
        if field["Progetto"] in issue["fields"] and issue["fields"][field["Progetto"]]:
            for el in issue["fields"][field["Progetto"]]["content"]:
                for el2 in el["content"]:
                    if "text" in el2:
                        progetto += el2["text"] + " "
        note = ""
        if field["Note"] in issue["fields"] and issue["fields"][field["Note"]]:
            for el in issue["fields"][field["Note"]]["content"]:
                for el2 in el["content"]:
                    if "text" in el2:
                        note += el2["text"] + " "
                    
        sts = ""
        if field["STS"] in issue["fields"] and issue["fields"][field["STS"]]:
            for el in issue["fields"][field["STS"]]["content"]:
                for el2 in el["content"]:
                    sts += el2["text"] + " "
        asse = ""
        if field["Assegnatario"] in issue["fields"] and issue["fields"][field["Assegnatario"]]:
            for el in issue["fields"][field["Assegnatario"]]:
                asse = ' '.join(issue["fields"][field["Assegnatario"]])
        if key:
            df = pd.concat([pd.DataFrame([[key[0],issue["fields"]["summary"],issue["fields"]["issuetype"]["name"],progetto,note,issue["fields"]["priority"]["name"],issue["fields"]["status"]["name"],asse,sts]], columns=df.columns), df], ignore_index=True)
        else:
            df = pd.concat([pd.DataFrame([["notKey",issue["fields"]["summary"],issue["fields"]["issuetype"]["name"],progetto,note,issue["fields"]["priority"]["name"],issue["fields"]["status"]["name"],asse,sts]], columns=df.columns), df], ignore_index=True)
    return df
           

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello, FastAPI!"}
    
def question2jql(msg: str):
    result = agent.invoke(f"{msg}")
    print("JQL = ", result["intermediate_steps"][0][0].tool_input)
    return result["intermediate_steps"][0][0].tool_input
  
@app.post("/jira")
def getjira(msg: str):
    df = get_jira_issues(question2jql(msg),50)
    df2 = df.groupby(['Tipo Ticket'],as_index=False).size()
    df3 = df.groupby(['Stato'],as_index=False).size()
    df4 = df.groupby(['Priorità'],as_index=False).size()
    
    res = {}
    res["issues number"] = len(df)
    res["statistics"] = {
        'tipotickets': json.loads(df2.to_json(orient="records")),
        'statotikets': json.loads(df3.to_json(orient="records")),
        'priorità': json.loads(df4.to_json(orient="records")),
        }
    res["issues"] = json.loads(df.to_json(orient="records"))
    return res

   
if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8080)
