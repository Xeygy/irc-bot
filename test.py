from bs4 import BeautifulSoup
import requests

url = "https://wiki.leagueoflegends.com/en-us/Aphelios"
res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")

print(soup)

# for i in soup.findall("h2"):
#     print(i)