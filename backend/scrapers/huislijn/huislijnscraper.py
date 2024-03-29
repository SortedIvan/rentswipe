import requests
from bs4 import BeautifulSoup
from utility_data.rental_listing_data import RentalListing
import uuid
import re

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
url_base = 'https://www.huislijn.nl'

urls = {
    "amsterdam": "/noord-holland/amsterdam?c-houseFrom=-1",
    "rotterdam":"/zuid-holland?c-houseFrom=-1&c-municipality=Rotterdam",
    "den-haag": "/zuid-holland/den-haag?c-houseFrom=-1",
    "utrecht": "/utrecht?c-houseFrom=-1&c-municipality=Utrecht",
    "eindhoven": "/noord-brabant/eindhoven?c-houseFrom=-1",
    "tilburg": "/noord-brabant?c-houseFrom=-1&c-municipality=Tilburg",
    "almere": "/flevoland?c-houseFrom=-1&c-municipality=Almere",
    "groningen": "/groningen?c-houseFrom=-1&c-municipality=Groningen",
    "breda": "/noord-brabant?c-houseFrom=-1&c-municipality=Breda",
    "nijmegen": "/gelderland?c-houseFrom=-1&c-municipality=Nijmegen",
    "enschede": "/overijssel?c-houseFrom=-1&c-municipality=Enschede",
    "apeldoorn": "/gelderland?c-houseFrom=-1&c-municipality=Apeldoorn",
    "haarlem": "/noord-holland/haarlem?c-houseFrom=-1",
    "arnhem": "/gelderland/arnhem?c-houseFrom=-1",
    "gemeente-zaanstad": "/noord-holland?c-houseFrom=-1&c-municipality=Zaanstad",
    "amersfoort": "/utrecht?c-houseFrom=-1&c-municipality=Amersfoort",
    "gemeente-haarlemmermeer": "/noord-holland?c-houseFrom=-1&c-municipality=Haarlemmermeer",
    "den-bosch": "/noord-brabant?c-houseFrom=-1&c-municipality=%27s-Hertogenbosch",
    "zoetermeer": "/zuid-holland/zoetermeer?c-houseFrom=-1",
    "zwolle": "/overijssel/zwolle?c-houseFrom=-1"
}


def GetHuislijnHtml(city, page):
    if page == 1:
        full_url = 'https://www.huislijn.nl/huurwoning/nederland' + urls[city]
        return requests.get(full_url, headers=headers)
    full_url = 'https://www.huislijn.nl/huurwoning/nederland' + urls[city] + f'?page={page}'
    return requests.get(full_url, headers=headers)

def ConvertHuislijnHtml(city):
    results = []
    soups = []
    #TODO: Change page not be a constant
    for i in range(1, 5):
        results.append(GetHuislijnHtml(city, i))
    for i in range(len(results)):
        soups.append(BeautifulSoup(results[i].text, "html.parser"))
    return soups

def GetHuislijnLinksAndImages(city):
    huislijn_soups = ConvertHuislijnHtml(city)
    links = []
    for soup in huislijn_soups:
        all_listings = soup.find_all('div', attrs = {'class': 'object-panel'})
        for listing in all_listings:
            for a in listing.find_all('a', href = True):
                link = a['href']

            img_obj = listing.find('img')
            if img_obj.has_attr('src'):
                image_url = img_obj['src']
            else: image_url = "Empty"
            
            links.append((link, image_url))
    return links

def GetHuislijnRentalListingSoups(city):
    huislijn_property_links = GetHuislijnLinksAndImages(city)
    final_listing_soups = []
    
    for i in range(len(huislijn_property_links)):
        final_listing_soups.append(BeautifulSoup(requests.get(url_base + huislijn_property_links[i][0], headers=headers).text,  "html.parser"))

    return (final_listing_soups,huislijn_property_links)


def GetHuislijnRentalListings(city):
    #TODO: Make this into one function call
    soups_and_links = GetHuislijnRentalListingSoups(city)
    huislijn_properties_soups = soups_and_links[0]
    huislijn_property_links =  soups_and_links[1]

    rental_listings = []

    for i in range(len(huislijn_properties_soups)):
        address_and_name = huislijn_properties_soups[i].find('div', attrs = {'class': 'address'})
        name = address_and_name.find('span', attrs = {'class': 'address-line'}).text.split()
        address_and_zip = address_and_name.find('span', attrs = {'class': 'second-line'})
        zip = address_and_zip.find('span', attrs = {'class': 'zip'}).text.split()
        address = address_and_zip.find('span', attrs = {'class': 'place'}).text.split()
        price = huislijn_properties_soups[i].find('div', attrs = {'class':'pricing'}).text.split()


        #TODO: Change sqm_property to be one value for evertyhing
        try: # We attempt to find the SQM in the address string
            if city == "den-haag" or city == "den-bosch":
                sqm_property = re.findall("\d+", str(address[2]))
            else: 
                sqm_property = re.findall("\d+", str(address[1]))
            print(sqm_property)
            sqm_property = sqm_property[0]
        except: # In case that it is not found, we replace with 0 (or Unavaiable)
            sqm_property = 20

        if type(name) is list:
            name = ' '.join(name)
        if type(address) is list:
            address = ''.join(address)
        if type(price) is list:
            price = ''.join(price)
            if not price.__contains__("Ikwilmeerinformatieoverdezehuurwoning"):
                price = price.replace('€', '')
            if price.__contains__("Ikwilmeerinformatieoverdezehuurwoning"):
                price = price.replace("Ikwilmeerinformatieoverdezehuurwoning", "")
                price = price.replace('€', '')

        price = ''.join(filter(lambda i: i.isdigit(), price))
        sqm = sqm_property
        if (type(zip) is list):
            zip = ''.join(zip)

        city = city.lower() # Ensuring that cities are one format
        rental_listings.append(
            RentalListing(
                str(uuid.uuid4()),
                "Rental property",
                name,
                "Today",
                int(price),
                int(sqm),
                "Unavailable",
                "None",
                "https://www.huislijn.nl" + huislijn_property_links[i][0],
                name + " " + zip,
                city,
                huislijn_property_links[i][1] # IMAGE LINK
            )
        )
    return rental_listings
