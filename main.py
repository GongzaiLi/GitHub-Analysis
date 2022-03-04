# pip install requests
# https://docs.github.com/en/rest/reference/search

import requests
import csv
import time

STARTS_NUMBER = 10000

PER_PAGE = 1
PAGE = 1

HEADER = ['Project Name', 'URL', 'Language', 'Forks', 'Watchers', 'Size Byte', 'Stars', 'Topics',
          'Contributors', 'Type']  # , 'Contributors'

NOT_PROGRAMMING_LANGUAGE = ["Markdown", None]
# todo add the 加一些多的内容和 对应的 characteristic 
WEB_APPLICATION_CHARACTERISTIC = ["frontend", "react", "framework", "backend", "api", "web", "apis", "webapp",
                                  "web", "html", "css", "http-client", "browser", "angular", "html5", "vue",
                                  "webfont"]

FRAMEWORK_CHARACTERISTIC = ["framework", "plugin-framework", "python-framework"]

AI_CHARACTERISTIC = ["deep-learning", "machine-learning", "neural-network"]

MOBILE_APPLICATION_CHARACTERISTIC = ["android", "ios"]

CHARACTERISTICS = [WEB_APPLICATION_CHARACTERISTIC, FRAMEWORK_CHARACTERISTIC, AI_CHARACTERISTIC,
                   MOBILE_APPLICATION_CHARACTERISTIC]

PROJECT_CATEGORIES = {-1: "Other", 0: "Web Application", 1: "Framework", 2: "AI", 3: "Mobile App"}


# STATIC_LANGUAGE = ["C++"]
# DYNAMIC_LANGUAGE = ["JavaScript", "TypeScript", "Python"]


def get_github_response(url, http_header):
    try:
        res = requests.get(url, headers=http_header)
        print(f"Status Code {res.status_code}")
        # curl -H "Authorization: token OAUTH-TOKEN" https://api.github.com
        # print(res.headers)
        if res.status_code != 200:  # curl -u "username" https://api.github.com
            return None
        response_dic = res.json()
        print(f"Total Count: {response_dic['total_count']}")

        response_items = response_dic['items']
        print(f"Total Items: {len(response_items)}")
        return response_items
    except Exception as e:
        print(f"get_github_response Error Message {e}")
        exit(1)


def procces_item(items, http_headers):
    data = []
    for item in items:
        project_name = item['full_name']
        url = item['html_url']
        # "languages_url": "https://api.github.com/repos/freeCodeCamp/freeCodeCamp/languages",
        language = item['language']
        if language in NOT_PROGRAMMING_LANGUAGE:
            continue
        forks = item['forks']
        watchers = item['watchers']
        size = item['size']
        contributors = count_contributors_response(item['contributors_url'], http_headers)
        stars = item['stargazers_count']
        topic = f"{', '.join(map(str, item['topics']))}"
        project_category = f"{', '.join(map(str, project_category_check(item['topics'])))}"
        data.append([project_name, url, language, forks, watchers, size, stars, topic, contributors, project_category])
    return data


def count_contributors_response(contributor_url, http_headers):
    try:
        # {contributor_url}?per_page=100&page={page}
        res = requests.get(f"{contributor_url}?per_page=1&anon=true", headers=http_headers)

        if res.status_code != 200:  # curl -u "username" https://api.github.com
            print(F"Contributor Status Code {res.status_code}")
            return None  # The history or contributor list is too large to list contributors for this repository via the API.

        print(res.headers)
        link = res.headers['link']
        count = int(link.split("page=")[-1].split(">")[0])
        print(count)
        # print(res.headers)
        return count
    except Exception as e:
        print(f"count_contributors_response Error Message {e}")
        return None


def write_in_csv(data, page, filename):
    with open(filename, 'a+', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        if page == 1:
            print("Here Writing")
            writer.writerow(HEADER)
        writer.writerows(data)
        print(data)
        print(f"================= write done in {page} ==========================")
        # time.sleep(5)


def project_category_check(item_topics):
    project_category = set()
    for topic in item_topics:
        for index, character in enumerate(CHARACTERISTICS):
            if any(topic.lower() == character or character in topic.lower() for character in character):
                project_category.add(PROJECT_CATEGORIES[index])

    if len(project_category) == 0:
        project_category.add(PROJECT_CATEGORIES[-1])  # Other
    return list(project_category)


if __name__ == '__main__':
    # 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
    http_headers = {"Authorization": "token " + "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",
                    'Accept': 'application/vnd.github.v3+json'}
    top = 1000
    filename = F"github_info_stars_over_{STARTS_NUMBER}_top_{top}.csv"

    while True:

        if PAGE == 1001 or PAGE > top:
            print("=====================================end=================================")
            exit(1)

        print(f"Start Page {PAGE}")
        url = f"https://api.github.com/search/repositories?per_page={PER_PAGE}&page={PAGE}&q=stars%3A>{STARTS_NUMBER}"
        response_items = get_github_response(url, http_headers)
        if response_items is None:
            print(f"---------------------------Re fetch it {PAGE}----------------------------")
            time.sleep(5)
            continue

        if len(response_items) == 0:
            print("=====================================end=================================")
            exit(1)

        data = procces_item(response_items, http_headers)
        write_in_csv(data, PAGE, filename)
        PAGE += 1
