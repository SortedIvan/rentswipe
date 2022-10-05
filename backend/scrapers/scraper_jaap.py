import requests
from bs4 import BeautifulSoup

jaap_listing_urls = []


class JaapListing():
    def __init__(self, url, houseName, houseLocation, housePrice,houseType,houseMetrics, nrOfRooms,interior, option):
        self.url = url
        self.houseName = houseName
        self.houseLocation = houseLocation
        self.housePrice = housePrice
        self.houseType = houseType
        self.houseMetrics = houseMetrics
        self.nrOfRooms = nrOfRooms
        self.interior = interior
        self.option = option

def get_jaap_urls():
    with open('jaap_nl_areas.txt') as my_file:
        for line in my_file:
            jaap_listing_urls.append(line[:-2])
        return jaap_listing_urls
 

def match_string_to_url(name, urls):
    for i in range(len(urls)):
        if urls[i].find(name) != -1:
            return urls[i]
    return ""


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
def get_jaap_html(city, price_low, price_high, km, page_nr):
    jaap_listing_urls = get_jaap_urls()
    url = match_string_to_url(city, jaap_listing_urls)
    full_url = f'https://www.jaap.nl/huurhuizen/{url}/+{km}km/{price_low}-{price_high}/p{page_nr}'
    print(full_url)
    return requests.get(full_url, headers=headers)


def get_jaap_soups(city, priceLow, priceHigh, km):
    results = []
    soups = []
    for i in range(10):
        results.append(get_jaap_html(city, priceLow, priceHigh,km,i))
    for i in range(len(results)):
        soups.append(BeautifulSoup(results[i].text, "html.parser"))
    return soups


def get_raw_jaap_listings(city, priceLow, priceHigh, km):
    soups = get_jaap_soups(city, priceLow, priceHigh, km)
    rawlistings = []
    for i in range(len(soups)):
        list_of_results = soups[i].find('div', attrs={'class': 'property-list'})
        actual_listings = list_of_results.find_all('div', attrs= {'class' : 'property'})
        rawlistings.append(actual_listings)
    return rawlistings

def TestSoup():
    types_of_houses = ["Eengezinswoning", "Benedenwoning", "Kamer", "Appartement","Bovenwoning", "Garage","Woning", "Studio"]
    result = BeautifulSoup(get_jaap_html("eindhoven", 100, 1000, 10, 1).text, "html.parser")
    newResult = result.find('div', attrs={'class': 'property-list'})
    listings = newResult.find_all('div', attrs= {'class' : 'property'})

    for i in range(len(listings)):
        if listings[i].find('a', attrs = {'class': 'property-inner'}) is not None:
            url = listings[i].find('a', attrs = {'class' : 'property-inner'}, href = True)['href']
        if listings[i].find('div', attrs = {'class': 'property-info'}) is not None:
            property_info_list = listings[i].find('div', attrs = {'class': 'property-info'})
            property_name = property_info_list.find('h2', attrs = {'class' : 'property-address-street'}).text
            property_location = property_info_list.find('div', attrs = {'class' : 'property-address-zipcity'}).text
            property_price = property_info_list.find('div', attrs = {'class' : 'property-price'}).text
            property_features = property_info_list.find_all('div', attrs = {'class': 'property-feature'})
            for i in range(len(property_features)):
                if (property_features[i].text.find("kamer") != -1):
                    property_room_amount = property_features[i]
                elif (property_features[i].text.find("m²") != -1):
                    property_size = property_features[i]
                else:
                    for k in range(len(types_of_houses)):
                        if str(property_features[i].text).find(str(types_of_houses[k]) != -1):
                            property_type = property_features[i].text
#Eengezinswoning, Benedenwoning, Kamer, Appartement,Bovenwoning, Garage,Woning, Studio
        print(str(url))
        print(property_name)
        print(property_location)
        print(property_price)
        print(str(property_type))
        print(property_room_amount)
        print(property_size)

    
    #return listings
    #listings = []
    #listings.append(result.find_all("div", attrs={'class' : 'property'}))

TestSoup()

#print(get_raw_jaap_listings("eindhoven", 100, 1000, 10))