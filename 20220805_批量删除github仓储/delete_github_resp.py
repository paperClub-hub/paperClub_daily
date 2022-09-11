
from time import sleep
import requests

TOKEN = 'ghp_M3LkdqNUishqUmdxoVvw8kKHm6rQCf16b' # 生成的token


def delete_rep(rep_url):
    HEADERS = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {TOKEN}",  # 粘贴 github delete-token
        "X-OAuth-Scopes": "repo"
    }
    requests.delete(url=rep_url, headers=HEADERS) # 仓储删除
    sleep(2)



if __name__ == '__main__':
    reps = ['image-search-engine','Machine-Reading-Comprehension']
    base_url = 'https://api.github.com/repos/paperClub-hub'
    for rep in reps:
        rep_url = f"{base_url}/{str(rep).strip()}"
        delete_rep(rep_url)

