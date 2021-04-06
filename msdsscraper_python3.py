import sys
import getopt
import requests
import csv
import re
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import logging
import time
import os.path
import random

user_agent_list = [
   #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

def scrape_msds_sigma(caslist, notfound, language):
	print("Scraping Sigma-Aldrich")
	for row in caslist:
		for cas in row:
			if(os.path.isfile("".join([cas, ".pdf"]))):
				print("".join([cas, " molecule MSDS already found in current directory. Skipping"]))
				break
			time.sleep(random.randrange(1,10))
			searchpageresp = requests.get(''.join(["https://www.sigmaaldrich.com/catalog/search?term=",cas,"&interface=CAS%20No.&N=0&mode=match%20partialmax&lang=",language,"&region=PL&focus=product"]), timeout=10)
			searchsoup = BeautifulSoup(searchpageresp.content, 'html.parser')
			searchpageresp.close()
			products = searchsoup.find_all("div", class_="productContainer")
			foundflag = False
			for product in products:
				productinfo = ''
				try:
					productinfo = product.find("li", class_="substance-display-attributes").get_text()
				except:
					foundflag = False
				casnum = re.findall("(?<=CAS Number:\s)[0-9-]+", productinfo)
				if(len(casnum)>0 and casnum[0] == cas):
					productnum = product.find("div", class_="product-listing-outer").find("li", class_="productNumberValue").get_text().strip()
					print("".join(["CAS: ", cas, " found: ", casnum[0]," product number: ", productnum]))
					foundflag = download_msds_sigma(cas, productnum, language)
					break
			if(foundflag is False):
				print("".join([cas, " product not found. Appended to remaining list."]))
				notfound.append([cas])

def scrape_msds_tci(caslist, notfound, language):
	print("Scraping TCI Chemicals")
	for row in caslist:
		for cas in row:
			if(os.path.isfile("".join([cas, ".pdf"]))):
				print("".join([cas, " molecule MSDS already found in current directory. Skipping"]))
				break
			time.sleep(random.randrange(1,10))
			searchpageresp = requests.get(''.join(["https://www.tcichemicals.com/OP/en/search/?text=",cas]), headers={'User-agent': random.choice(user_agent_list)}, timeout=10)
			searchsoup = BeautifulSoup(searchpageresp.content, 'html.parser')
			searchpageresp.close()
			products = searchsoup.find_all("div", class_="prductlist selectProduct")
			foundflag = False
			for product in products:
				productinfo = ''
				try:
					productinfo = product.find("table", class_="font12 mb20").get_text()
				except:
					foundflag = False
				casnum = re.findall("(?<=CAS RN\s)[0-9-]+", productinfo)
				if(len(casnum)>0 and casnum[0] == cas):
					productnum = re.findall("(?<=Product Number\s).+", productinfo)
					print("".join(["CAS: ", cas, " found: ", casnum[0]," product number: ", productnum[0]]))
					foundflag = download_msds_tci(cas, productnum[0], language)
				break
			if(foundflag is False):
				print("".join([cas, " product not found. Appended to remaining list."]))
				notfound.append([cas])

def scrape_msds_alfa(caslist, notfound, language):
	print("Scraping Alfa Aesar")
	for row in caslist:
		for cas in row:
			if(os.path.isfile("".join([cas, ".pdf"]))):
				print("".join([cas, " molecule MSDS already found in current directory. Skipping"]))
				break
			time.sleep(random.randrange(1,10))
			searchpageresp = requests.get(''.join(["https://www.alfa.com/en/search/?search-tab=product-search-container&type=SEARCH_CHOICE_CAS&q=",cas]), headers={'User-agent': random.choice(user_agent_list)}, timeout=10, allow_redirects=False)
			searchsoup = BeautifulSoup(searchpageresp.content, 'html.parser')
			searchpageresp.close()
			foundflag = False
			# single result
			if 'location' in searchpageresp.headers:
				#print(searchpageresp.headers['location'])
				productnum = re.findall('(?<=catalog/)[\w\d]+', searchpageresp.headers['location'])
				print("".join(["CAS: ", cas, "found. Product number: ", productnum[0].lstrip("0")])) #strip leading 0 to get exact product number
				foundflag = download_msds_alfa(cas, productnum[0].lstrip("0"), language)
			
			# multiple results
			else:
				products = searchsoup.find_all("div", class_="list-group-item")
				for product in products:
					productinfo = ''
					try:
						productinfo = product.get_text()
					except:
						foundflag = False
					casnum = re.findall("(?<=CAS:\s)[0-9-]+", productinfo)
					if(len(casnum)>0 and casnum[0] == cas):
						productnum = product.find("div", class_="search-result-number").get_text()
						print("".join(["CAS: ", cas, " found: ", casnum[0]," product number: ", productnum[0]]))
						foundflag = download_msds_alfa(cas, productnum[0], language)
					break
			if(foundflag is False):
				print("".join([cas, " product not found. Appended to remaining list."]))
				notfound.append([cas])
def download_msds_sigma(cas, productnum, lang):
	time.sleep(random.randrange(1,10))
	with requests.Session() as sess:
		acceptlang = ''.join([lang, ",en-US;q=0.7,en;q=0.3"])
		headers = {	'User-agent': random.choice(user_agent_list),
					'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					'Accept-Encoding': 'gzip, deflate, br',
					'Accept-Language': acceptlang,
					'DNT' : '1'}
		sess.headers.update(headers)
		payload = {	'requestMsds': 'true',
					'productNumber': productnum,
					'PageToGoToURL': '/safety-center.html',
					'btnGo1.x': '1',
					'country': '',
					'language': '',
					'brand': ''}
		msdssearchpage = sess.get("https://www.sigmaaldrich.com/safety-center.html")
		time.sleep(random.randrange(1,10))
		msdspageresp = ''
		#print(msdssearchpage.cookies)
		try:
			msdspageresp = sess.post("https://www.sigmaaldrich.com/catalog/DisplayMSDSContent.do", headers={'Content-type': 'application/x-www-form-urlencoded', 'Connection': 'keep-alive', 'Host': 'www.sigmaaldrich.com', 'Origin':'https://www.sigmaaldrich.com', 'Referer':'https://www.sigmaaldrich.com/safety-center.html'}, data=payload, verify=True, timeout=10, allow_redirects=True)
		except:
			print("Error 2. MSDS page not found!")
			sess.close()
			return False
		if(len(msdspageresp.history) > 0 and msdspageresp.history[0].status_code == requests.codes.found):
			print("redirection")
			print(sess.cookies)
			try:
				redirection = sess.get(msdspageresp.history[0].headers['Location'], headers={'Host':'www.sigmaaldrich.com', 'Referer':'https://www.sigmaaldrich.com/safety-center.html'}, cookies={'Country':'POL', 'SialLocaleDef':'CountryCode~PL|WebLang~-24|'}, timeout=120)
			except:
				print("Error 2. MSDS page not found!")
				sess.close()
				return False
			print(str(redirection.content).find("SDS Not Found"))
			if(str(redirection.content).find("SDS Not Found")!=-1):
				print("Error 1. MSDS page not found!")
				sess.close()
				return False
			redirectionsoup = BeautifulSoup(redirection.content, 'html.parser')
			try:
				form = redirectionsoup.find("form", {'name':'msdsForm'})
				country = form.find("input", {'name':'country'})['value']
				language = form.find("input", {'name':'language'})['value']
				productnumber = form.find("input", {'name':'productNumber'})['value']
				brand = form.find("input", {'name':'brand'})['value']
				PageToGoURL = form.find("input", {'name':'PageToGoToURL'})['value']
			except:
				print("Error 2. MSDS page not found!")
				sess.close()
				return False
			params = {	'country': country, 'language':language, 'productNumber': productnum, 'brand': brand, 'PageToGoToURL': PageToGoURL}
			time.sleep(1)
			time.sleep(random.randrange(1,10))
			msdspage = sess.get('https://www.sigmaaldrich.com/MSDS/MSDS/DisplayMSDSPage.do', params=params, headers={'Host':'www.sigmaaldrich.com', 'Referer':redirection.url}, cookies={'Country':'POL', 'SialLocaleDef':'CountryCode~PL|WebLang~-24|'}, timeout=60)
			msdspagesoup = BeautifulSoup(msdspage.content, 'html.parser')
			try:
				file = sess.get("".join(["https://www.sigmaaldrich.com", msdspagesoup.find("iframe", id="msdsPageFrame")['src']]), headers={'Referer':msdspage.url}, timeout=60)
				open("".join([cas, ".pdf"]), 'wb').write(file.content)
			except:
				print("Error 3. MSDS page not found!")
				#print(msdspagesoup.prettify())
				sess.close()
				return False
		sess.close()
	return True

def download_msds_tci(cas, productnum, lang):
	time.sleep(random.randrange(1,10))
	with requests.Session() as sess:
		acceptlang = ''.join([lang, ",en-US;q=0.7,en;q=0.3"])
		producthref = ''.join(["https://www.tcichemicals.com/OP/en/p/", productnum])
		headers = {	'User-agent': random.choice(user_agent_list),
			'Accept': '*/*',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
			'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
		}
		sess.headers.update(headers)
		prodpage = sess.get(producthref)
		#print(prodpage.text)
		csrfToken = re.findall('(?<=ACC\.config\.CSRFToken = \')[\w\d-]+', prodpage.text)[0]
		#print(csrfToken)
		payload = {	'productCode': productnum,
					'langSelector': 'en',
					'selectedCountry': 'JP',
					'CSRFToken': csrfToken}
		#print(prodpage.cookies)
		try:
			msdspageresp = sess.post("https://www.tcichemicals.com/OP/en/documentSearch/productSDSSearchDoc", headers={'x-requested-with': 'XMLHttpRequest', 'Connection': 'keep-alive', 'Origin':'https://www.tcichemicals.com', 'Referer':'https://www.tcichemicals.com/OP/en/p/D0208'}, data=payload, verify=True, timeout=60, allow_redirects=True)
		except:
			print("Error 2. MSDS page not found!")
			sess.close()
			return False
		if 'Content-Disposition' not in msdspageresp.headers:
			print("Error 2. MSDS page not found!")
			sess.close()
			return False
		filehref = re.findall('(?<=;filename=).+', msdspageresp.headers['Content-Disposition'])[0]
		try:
			#print("".join(["https://www.tcichemicals.com/OP/en/sds/", filehref]))
			file = sess.get("".join(["https://www.tcichemicals.com/OP/en/sds/", filehref]), allow_redirects=True, timeout=60)
			open("".join([cas, ".pdf"]), 'wb').write(file.content)
		except Exception as e:
			print("Error 3. MSDS page not found!")
			#print(e)
			sess.close()
			return False
	return True

def download_msds_alfa(cas, productnum, lang):
	time.sleep(random.randrange(1,10))
	with requests.Session() as sess:
		acceptlang = ''.join([lang, ",en-US;q=0.7,en;q=0.3"])
		headers = {	'User-agent': random.choice(user_agent_list),
			'Accept': '*/*',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
			'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
		}
		sess.headers.update(headers)
		mainresp = sess.get("https://www.alfa.com") #get main page (since for some reason direct msds get will result in 404)
		if lang.lower() is "en":
			lang = "EE"
		try:
			file = sess.get("".join(["https://www.alfa.com/en/msds/?language=",lang,"&subformat=CLP1&sku=", productnum]), allow_redirects=True, timeout=60)
			open("".join([cas, ".pdf"]), 'wb').write(file.content)
		except Exception as e:
			print("Error 3. MSDS page not found!")
			#print(e)
			sess.close()
			return False
	return True

def resetDicts(caslist, notfound):
	caslist = notfound
	notfound = []

def main(argv):
	caslist = ''
	language = 'pl'
	notfound = []
	
	try:
		opts, args = getopt.getopt(argv,"hdi:o:",["ifile=","ofile=","language=","debug="])
	except getopt.GetoptError:
		print("No csv file with CAS numbers given")
		print("Usage: msdsscraper.py -i <input.csv> [options]")
		print("Type msdsscraper.py -h for help")
		exit(2)

	for opt, arg in opts:
		if(opt == "-h"):
			print("MSDS scraper. Takes a CAS number list and provides links to MSDS or downloads them.")
			print("Usage: msdsscraper.py -i <input.csv> [options=vars]")
			print("Options:")
			print("language=[pl] scrapes MSDS in specific language")
			print("-d shows debug messages")
		if(opt == "-i"):
			csvfile = open(arg)
			caslist = csv.reader(csvfile, delimiter=' ')
			print("CAS list loaded:")
		if(opt == "-d"):
			logging.basicConfig(level=logging.DEBUG)
	
	if(caslist == ''):
		print("No csv file with CAS numbers given")
		exit(2)


	scrape_msds_alfa(caslist, notfound, language)
	resetDicts(caslist, notfound)
	scrape_msds_tci(caslist, notfound, language)
	resetDicts(caslist, notfound)
	scrape_msds_sigma(caslist, notfound, language)

	print("Finished!")
	print("".join([str(len(notfound)), " compounds not found."]))
	with open("notfound.csv", "w") as exportfile:
		for cas in notfound:
			print("\""+cas+"\"", file=exportfile)
	

		
if __name__ == "__main__":
   random.seed()
   main(sys.argv[1:])