from bs4 import BeautifulSoup
import requests

url = 'http://blindy.tv'
#payload = {
#    'q': 'Python',
#}
r = requests.get(url )

soup = BeautifulSoup(r.text, "html.parser")
titles = soup.findAll('a', href=True)

#for t in titles:
#    if 'm3u' in t['href']:
#        print(t['href'])
#        print (t.string)

table = soup.find("table")
for row in table.findAll("tr"):
    cells = row.findAll("td")
    if len(cells) == 3:
        print (cells[2].find('a').get('href') )
        print (cells[1].text, "\n")
