from BeautifulSoup import BeautifulSoup
import urllib
#import lxml.html

def pnr_status(pnr_number):
    pnr_number = pnr_number.replace("-", "").strip()

    url = "http://www.indianrail.gov.in/cgi_bin/inet_pnrstat_cgi.cgi"
    params = {
	"lccp_pnrno1": str(pnr_number)
    }
    html = urllib.urlopen(url, urllib.urlencode(params)).read()
    soup = BeautifulSoup(html)
    table = soup.find(name="table", attrs={"id": "center_table"})    
    
    rows = parse_table(table)
    # first row is for header and last 2 rows for for chart prepared and comment    
    return rows[1:-2]

def parse_table(table):
    rows = table.findAll("tr")
    return [[extract_text(td) for td in tr.findAll("td")] for tr in rows]

def extract_text(elem):
    return "".join(elem.findAll(text=True)).strip()

