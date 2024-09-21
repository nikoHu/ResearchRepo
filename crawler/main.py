import requests
import csv
from datetime import datetime
import time
from typing import List, Dict
from requests.exceptions import RequestException

class GitHubScraper:
    def __init__(self, proxies: Dict[str, str] = None):
        self.base_url = "https://api.github.com/search/repositories"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "xxxx"  # 请替换为您的GitHub Token
        }
        self.proxies = proxies
        self.session = requests.Session()
        if self.proxies:
            self.session.proxies.update(self.proxies)
        
        self.keywords = {
            "Android": [
                "android", "androidstudio", "androiddev", "androidapp",
                "kotlin", "kotlinandroid", "androidjetpack", "jetpackcompose",
                "dagger", "rxjava", "rxandroid", "databinding", "viewbinding",
                "androidarchitecture", "mvvm", "roomdatabase", "workmanager",
                "navigationcomponent", "coroutines", "androidui", "materialdesign",
                "androidtesting", "espresso", "androidperformance", "androidndk"
            ],
            "Network": [
                "network", "networkprotocol", "tcpip", "httpclient", "restapi", "websocket",
                "socketprogramming", "networkingsecurity", "ssl", "tls",
                "oauth", "jwt", "vpn", "loadbalancer", "reverseproxy",
                "contentdeliverynetwork", "apigateway", "grpc", "microservices",
                "distributedcomputing", "networkmonitoring", "wireshark",
                "networksniffer", "packetanalysis", "networkperformance"
            ],
            "Database": [
                "database", "databasemanagement", "sql", "nosql", "orm", "jdbc", "jpa",
                "hibernate", "springdatajpa", "mysqljava", "postgresqljava",
                "mongodbdriver", "redisconnection", "cassandraclient",
                "neo4jbolt", "elasticsearchclient", "sqlitejava", "oracleconnection",
                "sqlserverjdbc", "databaseindexing", "databasesharding",
                "databasereplication", "databasetransaction", "databasemigration",
                "databasebackup", "databasesecurity"
            ]
        }
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
        self.api_calls = 0

    def update_rate_limit(self, response: requests.Response):
        self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
        self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', 0))
        self.api_calls += 1

    def wait_for_rate_limit(self):
        if self.rate_limit_remaining is not None and self.rate_limit_remaining == 0:
            wait_time = self.rate_limit_reset - int(time.time()) + 1
            if wait_time > 0:
                print(f"Rate limit reached. Waiting for {wait_time} seconds.")
                time.sleep(wait_time)

    def search_repositories(self, query: str, sort: str = "stars", order: str = "desc", per_page: int = 100, page: int = 1) -> Dict:
        self.wait_for_rate_limit()
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page
        }
        try:
            response = self.session.get(self.base_url, headers=self.headers, params=params)
            # print(f"API call made: {response.url}")
            self.update_rate_limit(response)
            
            if response.status_code == 403 and 'rate limit exceeded' in response.text:
                print("Rate limit exceeded. Waiting for reset.")
                self.wait_for_rate_limit()
                return self.search_repositories(query, sort, order, per_page, page)
            
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"An error occurred: {e}")
            return {"items": []}

    def get_last_commit_date(self, repo_url: str) -> str:
        try:
            commits_url = f"{repo_url}/commits"
            response = self.session.get(commits_url, headers=self.headers)
            self.update_rate_limit(response)
            response.raise_for_status()
            commits = response.json()
            if commits:
                return commits[0]['commit']['committer']['date']
        except RequestException as e:
            print(f"Error fetching last commit date: {e}")
        return None

    def categorize_project(self, project: Dict, category: str) -> bool:
        description = (project.get("description") or "").lower()
        topics = [topic.lower() for topic in project.get("topics", [])]
        name = project.get("name", "").lower()
        
        return any(keyword in description or keyword in topics or keyword in name for keyword in self.keywords[category])

    def save_to_csv(self, projects: List[Dict], filename: str, mode: str = 'a'):
        fieldnames = ["name", "url", "stars", "last_update", "description", "organization", "organization_url"]
        with open(filename, mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if mode == 'w':
                writer.writeheader()
            for project in projects:
                writer.writerow(project)

    def get_projects(self, category: str, total_count: int) -> List[Dict]:
        projects = {
            "stars:>=100": set(),
            "stars:10..99": set(),
            "stars:<10": set()
        }
        filename = f"{category.lower()}_projects.csv"
        self.save_to_csv([], filename, 'w')  # Initialize the CSV file

        target_counts = {
            "stars:>=100": int(total_count * 5 / 10),
            "stars:10..99": int(total_count * 3 / 10),
            "stars:<10": int(total_count * 2 / 10)
        }

        total_collected = 0
        start_time = time.time()
        last_report_time = start_time

        for keyword in self.keywords[category]:
            for star_range, target_count in target_counts.items():
                if len(projects[star_range]) >= target_count:
                    continue

                query = f"language:Java {keyword} {star_range}"
                page = 1
                while len(projects[star_range]) < target_count and page <= 10:
                    result = self.search_repositories(query, page=page)
                    
                    if not result.get("items"):
                        break  # No more results for this query

                    for item in result.get("items", []):
                        if len(projects[star_range]) >= target_count:
                            break

                        if self.categorize_project(item, category):
                            project_id = item["id"]
                            if project_id not in projects[star_range]:
                                last_commit_date = self.get_last_commit_date(item["url"])
                                project = {
                                    "name": item["name"],
                                    "url": item["html_url"],
                                    "stars": item["stargazers_count"],
                                    "last_update": last_commit_date,
                                    "description": item["description"] if item["description"] else None,
                                    "organization": item["owner"]["login"] if item["owner"]["type"] == "Organization" else None,
                                    "organization_url": item["owner"]["html_url"] if item["owner"]["type"] == "Organization" else None
                                }
                                projects[star_range].add(project_id)
                                self.save_to_csv([project], filename)

                                total_collected += 1
                                if total_collected % 50 == 0:
                                    current_time = time.time()
                                    time_taken = current_time - last_report_time
                                    print(f"\nProgress: Collected {total_collected} {category} projects.")
                                    print(f"Time taken for last 50 projects: {time_taken:.2f} seconds")
                                    for sr, project_set in projects.items():
                                        print(f"  {sr}: {len(project_set)}/{target_counts[sr]}")
                                    last_report_time = current_time

                    page += 1
                    time.sleep(2)  # 减少等待时间，但保持一些间隔以尊重API限制

            if all(len(projects[sr]) >= target_counts[sr] for sr in projects):
                break

        # 检查是否达到目标数量，如果没有，打印警告
        total_collected = sum(len(project_set) for project_set in projects.values())
        if total_collected < total_count:
            print(f"\nWARNING: Could not reach the target count for {category}.")
            print(f"Collected {total_collected} projects out of {total_count} target.")
            print("Possible reasons:")
            print("1. Not enough projects matching the criteria")
            print("2. API rate limit reached")
            print("3. Network issues")
            print("\nConsider the following actions:")
            print("1. Expand your keyword list")
            print("2. Adjust your star range criteria")
            print("3. Increase the number of pages searched per query")
            print("4. Check your API rate limit and consider using authenticated requests if not already doing so")

        # 打印最终统计信息
        total_time = time.time() - start_time
        print(f"\nFinal statistics for {category}:")
        for star_range, project_set in projects.items():
            print(f"  {star_range}: {len(project_set)}/{target_counts[star_range]} ({len(project_set)/target_counts[star_range]*100:.2f}%)")

        print(f"Total {category} projects collected: {total_collected}/{total_count} ({total_collected/total_count*100:.2f}%)")
        print(f"Total time taken: {total_time:.2f} seconds")
        return [project for project_set in projects.values() for project in project_set]

    def run(self):
        categories = [
            ("Android", 3000),
            ("Network", 1000),
            ("Database", 1000)
        ]
        
        total_start_time = time.time()
        
        for category, count in categories:
            print(f"Starting to scrape {count} {category} projects...")
            category_start_time = time.time()
            _ = self.get_projects(category, count)
            category_end_time = time.time()
            category_time = category_end_time - category_start_time
            print(f"Time taken for {category} category: {category_time:.2f} seconds")
            print(f"API calls made: {self.api_calls}")
            print(f"Remaining API calls: {self.rate_limit_remaining}")
            print("---")

        total_end_time = time.time()
        total_time = total_end_time - total_start_time
        print(f"Total runtime for all categories: {total_time:.2f} seconds")
        print(f"Total API calls made: {self.api_calls}")

if __name__ == "__main__":
    # 设置代理，如果不需要代理，可以传入 None
    proxies = {
        "http": "http://127.0.0.1:10809",
        "https": "https://127.0.0.1:10809"
    }
    scraper = GitHubScraper(proxies)
    scraper.run()