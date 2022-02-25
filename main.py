# pip install requests
# https://docs.github.com/en/rest/reference/search

import requests
import csv
import datetime

STARTS_NUMBER = 45000
HEADER = ['Project Name', 'URL', 'Language', 'Forks', 'Watchers', 'Size Byte', 'Contributors', 'Stars', 'Topics']


# contributors_url
class GetGitHub:
    def __init__(self, url):
        self.url = url
        self.response_items = []
        self.getResponse()

    def getResponse(self):
        try:
            res = requests.get(self.url)
            print(f"Status Code {res.status_code}")

            if res.status_code != 200:  # curl -u "username" https://api.github.com
                exit(1)
            response_dic = res.json()
            print(f"Total Count: {response_dic['total_count']}")

            self.response_items = response_dic['items']
            print(f"Total Items: {len(self.response_items)}")
        except Exception as e:
            print(f"Error Message {e}")
            exit(1)


def procces_item(items):
    data = []
    for item in items:
        project_name = item['full_name']
        url = item['html_url']
        # "languages_url": "https://api.github.com/repos/freeCodeCamp/freeCodeCamp/languages",
        language = item['language']
        forks = item['forks']
        watchers = item['watchers']
        size = item['size']
        contributors = count_contributors(item['contributors_url'])
        stars = item['stargazers_count']
        topic = f"{item['topics']}"
        data.append([project_name, url, language, forks, watchers, size, contributors, stars, topic])
        print(data)
    return data


def count_contributors(contributor_url):
    count = 0
    # {contributor_url}?per_page=100&page={page}
    res = requests.get(f"{contributor_url}?per_page=1&anon=true")
    if res.status_code != 200:  # curl -u "username" https://api.github.com
        print(f"Contributor Status Code {res.status_code}")
        exit(1)
    res.headers['link']

    return count


def write_in_csv(data, page, filename):
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        if page == 1:
            print("Hearer Writing")
            writer.writerow(HEADER)
        writer.writerows(data)
        print(f"================= write done in {page} ==========================")


if __name__ == '__main__':

    date = datetime.datetime.now()
    filename = f"{date.strftime('%x')}-{date.strftime('%X')}.csv"
    page = 1
    while True:
        print(f"Start Page {page}")
        url = f"https://api.github.com/search/repositories?per_page=100&page={page}&q=stars%3A>{STARTS_NUMBER}"
        res = GetGitHub(url)

        if len(res.response_items) == 0:
            print("end")
            exit(1)

        data = procces_item(res.response_items)
        write_in_csv(data, page, filename)
        page += 1
