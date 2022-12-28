import requests
from bs4 import BeautifulSoup

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

def GetFundaRentalHtml(city, page):
    if page == 1:
        full_url = f'https://www.funda.nl/huur/{city}/1-dag/'
        return requests.get(full_url, headers=headers)
    full_url = f'https://www.funda.nl/huur/{city}/1-dag/p{page}'
    return requests.get(full_url, headers=headers)

def ConvertFundaRentalSoups(city):
    results = []
    soups = []
    #TODO: Change page not be a constant
    for i in range(1, 5):
        results.append(GetFundaRentalHtml(city, i))
    for i in range(len(results)):
        soups.append(BeautifulSoup(results[i].text, "html.parser"))
    return soups

def GetFundaRentalListingLinks(city):
    funda_soups = ConvertFundaRentalSoups(city)
    links = []
    for soup in funda_soups:
        search_content = soup.find('div', attrs = {'class': 'search-content-output'})
        search_content_listings = search_content.find_all('li', attrs = {'class': 'search-result'})
        for listing in search_content_listings:
            listing_content = listing.find('div', attrs = {'class': 'search-result-content'})
            listing_href = "https://www.funda.nl/" + listing_content.find('a', attrs = {'data-object-url-tracking': 'resultlist'}, href = True)['href']
            links.append(listing_href)
    return links

def GetFundaRentalListings(city):
    funda_listing_links = GetFundaRentalListingLinks(city)
    if funda_listing_links is None:
        return None

    for link in funda_listing_links:
        listing_html = requests.get(link, headers=headers)
        listing_soup = BeautifulSoup(listing_html.text, "html.parser")
        listing_header_details = listing_soup.find('div', attrs = {'class': 'object-header__details'})

        listing_title = listing_header_details.find('span', attrs={'class': 'object-header__title'}).text.strip()
        listing_subtitle = listing_header_details.find('span', attrs = {'class': 'object-header__subtitle fd-color-dark-3'}).text.strip()
        listing_price = listing_header_details.find('div', attrs = {'class': 'object-header__pricing fd-text-size-l fd-flex--bp-m fd-align-items-center'}).text.strip()
        listing_living_details = []

        listing_living_details_set = listing_header_details.find_all('span', attrs = {'class': 'kenmerken-highlighted__value fd-text--nowrap'})
        for listing_living_detail in listing_living_details_set:
            listing_living_details.append(listing_living_detail.text.strip())
        
        listing_deposit = listing_soup.find('dd',attrs= {'class': 'object-kenmerken-group-list'}).text.strip()

        print(listing_title)
        print(listing_subtitle)
        print(listing_price)
        print(listing_living_details)
        print(listing_deposit)

GetFundaRentalListings("amsterdam")