# pip install requests
# https://docs.github.com/en/rest/reference/search

import requests
import csv
import datetime
import time

STARTS_NUMBER = 40000
HEADER = ['Project Name', 'URL', 'Language', 'Forks', 'Watchers', 'Size Byte', 'Stars', 'Topics',
          'Contributors']  # , 'Contributors'


# contributors_url
class GetGitHub:
    def __init__(self, url, http_headers):
        self.url = url
        self.response_items = []
        self.http_headers = http_headers
        self.getResponse()

    def getResponse(self):
        try:
            res = requests.get(self.url, headers=self.http_headers)
            print(f"Status Code {res.status_code}")
            # curl -H "Authorization: token OAUTH-TOKEN" https://api.github.com
            print(res.headers)
            if res.status_code != 200:  # curl -u "username" https://api.github.com
                exit(1)
            response_dic = res.json()
            print(f"Total Count: {response_dic['total_count']}")

            self.response_items = response_dic['items']
            print(f"Total Items: {len(self.response_items)}")
        except Exception as e:
            print(f"Error Message {e}")
            exit(1)


def procces_item(items, http_headers):
    data = []
    for item in items:
        project_name = item['full_name']
        url = item['html_url']
        # "languages_url": "https://api.github.com/repos/freeCodeCamp/freeCodeCamp/languages",
        language = item['language']
        if language is None:
            continue
        forks = item['forks']
        watchers = item['watchers']
        size = item['size']
        contributors = count_contributors(item['contributors_url'], http_headers)
        stars = item['stargazers_count']
        topic = f"{item['topics']}"
        data.append([project_name, url, language, forks, watchers, size, stars, topic, contributors])
        time.sleep(2)
    return data


def count_contributors(contributor_url, http_headers):
    count = 0
    # {contributor_url}?per_page=100&page={page}
    res = requests.get(f"{contributor_url}?per_page=1&anon=true", headers=http_headers)

    if res.status_code != 200:  # curl -u "username" https://api.github.com
        print(F"Contributor Status Code {res.status_code}")
        exit(1)

    link = res.headers['link']
    count = int(link.split("page=")[-1].split(">")[0])
    print(count)
    # print(res.headers)

    return count


def write_in_csv(data, page, filename):
    with open(filename, 'a+', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        if page == 1:
            print("Here Writing")
            writer.writerow(HEADER)
        writer.writerows(data)
        print(data)
        print(f"================= write done in {page} ==========================")


if __name__ == '__main__':
    # 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
    http_headers = {"Authorization": "token " + "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"}
    date = datetime.datetime.now()
    # f"{date.month}-{date.day}-{date.year}_{date.strftime('%X')}.csv"
    filename = "item_data.csv"
    per_page = 1
    page = 1

    while True:
        print(f"Start Page {page}")
        url = f"https://api.github.com/search/repositories?per_page={per_page}&page={page}&q=stars%3A>{STARTS_NUMBER}"
        res = GetGitHub(url, http_headers)

        if len(res.response_items) == 0:
            print("end")
            exit(1)

        data = procces_item(res.response_items, http_headers)
        write_in_csv(data, page, filename)

        if page % 20 == 0:
            time.sleep(100)

        page += 1

