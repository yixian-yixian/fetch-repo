import requests
import argparse
import datetime

GITHUB_API_URL = "https://api.github.com"

def get_repos(org, token):
    repos = []
    page = 1
    headers = {"Authorization": f"token {token}"}

    while True:
        url = f"{GITHUB_API_URL}/orgs/{org}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        repos.extend(data)
        page += 1

    return repos

def get_last_commit_date(repo_full_name, token):
    headers = {"Authorization": f"token {token}"}
    url = f"{GITHUB_API_URL}/repos/{repo_full_name}/commits?per_page=1"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    if data:
        commit_date = data[0]["commit"]["committer"]["date"]
        return datetime.datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
    return None

def main():
    parser = argparse.ArgumentParser(description="Check GitHub org repos for inactivity.")
    parser.add_argument("org", help="GitHub organization name")
    parser.add_argument("--days", type=int, default=90, help="Threshold in days")
    parser.add_argument("--token", required=True, help="GitHub personal access token")

    args = parser.parse_args()

    repos = get_repos(args.org, args.token)
    threshold_date = datetime.datetime.utcnow() - datetime.timedelta(days=args.days)

    print(f"Checking {len(repos)} repositories...")
    for repo in repos:
        last_commit = get_last_commit_date(repo["full_name"], args.token)
        if last_commit and last_commit < threshold_date:
            print(f"{repo['full_name']}: last commit on {last_commit.date()}")

if __name__ == "__main__":
    main()
