import requests
from requests.auth import HTTPBasicAuth



def get_issues(data, project, startAT, limit):
    project_url = f"{data.domain_url}/rest/api/3/search?jql=project={project}&startAt={startAT}&maxResults={limit}&fields=key,summary,status,assignee,priority,reporter,issuetype"
    auth = HTTPBasicAuth(data.username, data.token)
    response = requests.get(project_url, auth=auth)
    _data = {}
    try:
        if response.status_code == 200:
            response = response.json()
            issues = response["issues"]
            filtered_issues = []
            for issue in issues:
                fields = issue["fields"]
                filtered_issue = {
                    "key": issue["key"],
                    "type": fields["issuetype"]["name"],
                    "summary": fields["summary"],
                    "status": fields["status"]["name"],
                    "assignee_name": fields["assignee"]["displayName"] if fields["assignee"] else None,
                    "priority": fields["priority"]["name"],
                    "reporter_name": fields["reporter"]["displayName"],
                }
                filtered_issues.append(filtered_issue)

            # Display results
            return filtered_issues
        else:
            return []
    except Exception as e:
        return []