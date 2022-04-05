import requests
import csv
import time

STARTS_NUMBER = 10000
PER_PAGE = 1
PAGE = 1
Top = 1000
HEADER = ['Project Name', 'URL', 'Forks', 'Open issues', 'Size Byte', 'Stars', 'Topics', 'Contributors', 'Language:']
NOT_PROGRAMMING_LANGUAGE = ["Markdown", None]


def get_github_response(url, http_header):
    try:
        res = requests.get(url, headers=http_header)
        print(f"Status Code {res.status_code}")
        # curl -H "Authorization: token OAUTH-TOKEN" https://api.github.com
        if res.status_code != 200:  # curl -u "username" https://api.github.com
            return None
        response_dic = res.json()
        print(f"Total Count: {response_dic['total_count']}")

        response_items = response_dic['items']
        print(f"Total Items: {len(response_items)}")
        return response_items
    except Exception as e:
        print(f"{'-' * 20} get_github_response Error Message {e} {'-' * 20}")
        return None


def procces_item(items, http_headers):
    data = []

    for item in items:

        if item['language'] in NOT_PROGRAMMING_LANGUAGE:
            continue

        project_name = item['full_name']
        url = item['html_url']
        forks = F"{item['forks']}"
        open_issues = F"{item['open_issues']}"
        size = F"{item['size']}"
        stars = F"{item['stargazers_count']}"
        topic = f"{', '.join(map(str, item['topics']))}"
        contributors = F"{count_contributors_response(item['contributors_url'], http_headers)}"
        # ['Project Name', 'URL', 'Forks', 'Open issues', 'Size Byte', 'Stars', 'Topics', 'Contributors', 'Language']
        item_data_raw = [project_name, url, forks, open_issues, size, stars, topic, contributors]
        language_list = get_project_languages(item['languages_url'], http_headers)
        data.append(item_data_raw + language_list)
    return data


def get_project_languages(languages_url, http_headers):
    while True:
        try:
            # {contributor_url}?per_page=100&page={page}
            res = requests.get(languages_url, headers=http_headers)
            if res.status_code != 200:  # curl -u "username" https://api.github.com
                print(F"{'-' * 20} Contributor Status Code {res.status_code} {'-' * 20}")
                time.sleep(5)
                continue
            response_dic = res.json()
            languages_total_count = sum(response_dic.values())
            languages = []
            for key, item in response_dic.items():
                languages_percent = item / languages_total_count
                if languages_percent > 0.00099:
                    languages += [key, f"{languages_percent}%"]
            return languages
        except Exception as e:
            print(F"{'-' * 20} get_project_languages Error Message {e} {'-' * 20}")
            time.sleep(5)
            continue


def count_contributors_response(contributor_url, http_headers):
    try:
        # {contributor_url}?per_page=100&page={page}
        res = requests.get(f"{contributor_url}?per_page=1&anon=true", headers=http_headers)
        if res.status_code != 200:  # curl -u "username" https://api.github.com
            print(F"{'-' * 20} {contributor_url} {'-' * 20}")
            print(F"{'-' * 20}Contributor Status Code {res.status_code} {'-' * 20}")
            # The history or contributor list is too large to list contributors for this repository via the API.
            time.sleep(5)
            return None
        link = res.headers['link']
        count = int(link.split("page=")[-1].split(">")[0])
        return count
    except Exception as e:
        print(F"{'-' * 20} count_contributors_response Error Message {e} {'-' * 20}")
        return None


def write_in_csv(data, page, filename):
    with open(filename, 'a+', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        if page == 1:
            writer.writerow(HEADER)
        writer.writerows(data)
        print(f"{'=' * 35} write done in {page} {'=' * 35}")


if __name__ == '__main__':
    # pip install requests
    # https://docs.github.com/en/rest/reference/search
    # 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 # token

    http_headers = {"Authorization": "token " + "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",
                    'Accept': 'application/vnd.github.v3+json'}

    filename = F"github_projects_stars_over_{STARTS_NUMBER}_top_{Top}.csv"

    res = requests.get("https://api.github.com/repos/freeCodeCamp/freeCodeCamp/languages", headers=http_headers)

    while True:
        if PAGE == 1001 or PAGE > Top:
            print(F"{'=' * 35}end{'=' * 35}")
            exit(1)

        print(f"Start Page {PAGE}")
        url = f"https://api.github.com/search/repositories?per_page={PER_PAGE}&page={PAGE}&q=stars%3A>{STARTS_NUMBER}"
        response_items = get_github_response(url, http_headers)
        if response_items is None:
            print(f"{'-' * 35} Re fetch it {PAGE} {'-' * 35}")
            time.sleep(5)
            continue

        if len(response_items) == 0:
            print(F"{'=' * 35}end{'=' * 35}")
            exit(1)

        data = procces_item(response_items, http_headers)
        write_in_csv(data, PAGE, filename)
        PAGE += 1
