import sys
import json
import subprocess
import os
import requests
from requests.auth import HTTPBasicAuth
from slugify import slugify
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv(".env.local"))


def main():
    JIRA_EMAIL = config("JIRA_EMAIL")
    JIRA_TOKEN = config("JIRA_TOKEN")
    JIRA_BOARD = config("JIRA_BOARD", default="33")
    JIRA_BASE_URL = config("JIRA_BASE_URL")
    STATUS_NAME = config("STATUS_NAME", default="En curso")
    TASKS_TYPES = config(
        "TASKS_TYPES",
        default="feat|fix|bugfix|config|refactor|build|ci|docs|test",
    )
    API_URL = f"/rest/agile/1.0/board/{JIRA_BOARD}/sprint"  # sprints from a board
    API_URL = JIRA_BASE_URL + API_URL
    BASIC_AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    HEADERS = {"Content-Type": "application/json;charset=iso-8859-1"}
    response = requests.get(API_URL, headers=HEADERS, auth=BASIC_AUTH)
    all_sprints = json.loads(response.text)
    sprints = []
    for iss in all_sprints["values"]:
        if iss["state"] == "active":
            sprints.append(iss["id"])
    current_sprint = sprints[0]
    if len(sprints) > 1:
        my_env = os.environ.copy()
        my_env["GUM_CHOOSE_HEADER"] = f"Choose a sprint:"
        result = subprocess.run(
            ["gum", "choose"] + sprints, stdout=subprocess.PIPE, text=True, env=my_env
        )
        current_sprint = result.stdout.strip()
        pass
    elif len(sprints) == 0:
        print("No active sprint found")
        sys.exit(1)

    API_URL = f"/rest/agile/1.0/sprint/{current_sprint}/issue"  # issues from a sprint
    API_URL = JIRA_BASE_URL + API_URL
    BASIC_AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    HEADERS = {"Content-Type": "application/json;charset=iso-8859-1"}
    response = requests.get(API_URL, headers=HEADERS, auth=BASIC_AUTH)

    data = json.loads(response.text)

    options = []
    for iss in data["issues"]:
        if (
            iss["fields"]["status"]["name"] == STATUS_NAME
            and iss["fields"]["assignee"]["emailAddress"] == JIRA_EMAIL
        ):
            options.append(iss["key"])

    menu = ["Task selection", "Description", "Type", "Apply and exit"]
    values = {"Task selection": None, "Description": None, "Type": None}

    flag = True
    while flag:
        my_env = os.environ.copy()
        my_env["GUM_CHOOSE_HEADER"] = f"Choose a config option:"
        result = subprocess.run(
            ["gum", "choose"] + menu, stdout=subprocess.PIPE, text=True, env=my_env
        )

        match result.stdout.strip():
            case "Task selection":
                my_env = os.environ.copy()
                my_env["GUM_CHOOSE_HEADER"] = f"Choose a task to work on:"
                opt = subprocess.run(
                    ["gum", "choose"] + options,
                    stdout=subprocess.PIPE,
                    text=True,
                    env=my_env,
                )
                values["Task selection"] = opt.stdout.strip()
            case "Description":
                my_env["GUM_INPUT_HEADER"] = f"Enter the description:"
                opt = subprocess.run(
                    ["gum", "input", "--placeholder", """Description"""],
                    stdout=subprocess.PIPE,
                    text=True,
                    env=my_env,
                )
                values["Description"] = slugify(opt.stdout.strip())

            case "Type":
                my_env["GUM_CHOOSE_HEADER"] = f"Choose task type:"
                task_types = TASKS_TYPES.split("|")
                opt = subprocess.run(
                    ["gum", "choose"] + task_types,
                    stdout=subprocess.PIPE,
                    text=True,
                    env=my_env,
                )
                values["Type"] = opt.stdout.strip()
            case "Apply and exit":
                actual = [k for k, v in values.items() if v is None]
                if len(actual) > 0:
                    print(f"Missing values: {actual}")
                    continue
                else:
                    print("Applying changes")
                    print(values)
                    flag = False


if __name__ == "__main__":
    main()
