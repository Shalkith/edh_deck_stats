import requests
from bs4 import BeautifulSoup
from selenium import webdriver

import re
import time


class Card:
    def __init__(self,found,detail):
        self.synergy = 0
        self.synergized_cards = []
        self.available_synergy = 0
        self.highlander_points = 0
        
        if found == False:
            self.name = detail
            self.found = 'Card not Found'
        else:
            self.name = detail['name']
            self.found = found
            if detail['prices']['usd']==None:
                self.cost = detail['prices']['usd_foil']
            else:
                self.cost = detail['prices']['usd']
            self.legal = detail['legalities']['commander']
            self.cmc = detail['cmc']
            self.type = detail['type_line']
            self.image = detail['image_uris']['normal']
            try:
                self.rank = detail['edhrec_rank']
            except:
                self.rank = 'unranked'

                
def search(data):
    url = 'https://api.scryfall.com'
    search = '/cards/search'
    cardname = data
    #print(url+search+'?q="'+data+'"&unique=art')
    data = requests.get(url+search+'?q="'+data+'"&unique=art')
    
    price = 'undefined'
    pricecheck = 'undefined'
    selectedcard = ''
    found = False
    try:
        if data.json()['code'] == 'not_found':
            return cardname,found
    except:
        pass
    
    for card in data.json()['data']:
        #print(card['prices'])
        if card['prices']['usd'] == None and card['prices']['usd_foil'] == None:
            pass
        elif card['prices']['usd'] == None:
            pricecheck = card['prices']['usd_foil']
        else:
            pricecheck = card['prices']['usd']
        #print(pricecheck)
        if (price == 'undefined' or pricecheck < price) and cardname.lower() == card['name'].lower():
            selectedcard = card
            price = pricecheck
            found = True
    return selectedcard,found


def edhrec_scrape(card):
    scrapeurl = 'https://edhrec.com/cards/%s' % re.sub(r'[^A-Za-z0-9]+-', '', card.name.replace(" ","-").replace("'","").lower())

    driver.get(scrapeurl)
    driver.maximize_window()

    #hsc = driver.find_element_by_id("highsynergycards")
    #hsc = hsc.find_elements_by_class_name("Card_container__3ZpdL")
    time.sleep(5)
    try:

        page = driver.page_source
        time.sleep(3)
        try:
            driver.find_element_by_link_text("High Synergy Cards").click()
        except:
            pass

        while page != driver.page_source:
            page = driver.page_source
            try:
                driver.find_element_by_link_text("High Synergy Cards").click()
            except:
                pass
            print('page loading...')
            time.sleep(3)
        page = driver.page_source                
        soup = BeautifulSoup(page, 'html5lib')
        hsc = soup.find("div", {"id": "highsynergycards"})
        oldcard = ''
        cards = hsc.find_all("div")
        print('card data found in hsc:',len(cards))
        syn_cards = []
        for syncard in cards:
            
            if "Card_name" in str(syncard):
                found = False

                for item in syn_cards:
                    if syncard.text in item:
                        syn_cards[syn_cards.index(item)]=syncard.text
                        found = True
                if found == False:
                    syn_cards.append(syncard.text)



        #print('Available Synergy!',syn_cards)

        for deckitem in deckstats:
            if deckitem.name in syn_cards:
                card.synergy = card.synergy + 1
                card.synergized_cards.append(deckitem.name)
            card.available_synergy = len(syn_cards) 

        print(card.name)
        print(card.synergized_cards)
        print(card.synergy,"out of",card.available_synergy,"cards synergized")

    except Exception as e:
        print(card.name)
        print('Error',e)


    #input('paused at hsc')


    #print(soup.prettify())
    


canadian_highlander_cards = [
["Ancestral Recall",7],
["Balance",1],
["Birthing Pod",2],
["Black Lotus",7],
["Crop Rotation",1],
["Demonic Tutor",4],
["Dig Through Time",1],
["Flash",5],
["Gifts Ungiven",2],
["Imperial Seal",1],
["Intuition",1],
["Library of Alexandria",1],
["Mana Crypt",4],
["Mana Drain",1],
["Mana Vault",1],
["Merchant Scroll",1],
["Mind Twist",1],
["Mox Emerald",3],
["Mox Jet",3],
["Mox Pearl",3],
["Mox Ruby",3],
["Mox Sapphire",3],
["Mystical Tutor",2],
["Natural Order",4],
["Price of Progress",1],
["Protean Hulk",3],
["Sol Ring",4],
["Spellseeker",2],
["Strip Mine",3],
["Summoner’s Pact",1],
["Survival of the Fittest",2],
["Tainted Pact",1],
["Time Vault",7],
["Time Walk",7],
["Tinker",3],
["Tolarian Academy",1],
["Transmute Artifact",1],
["Treasure Cruise",1],
["True-Name Nemesis",1],
["Umezawa’s Jitte",2],
["Underworld Breach",1],
["Vampiric Tutor",2],
["Wishclaw Talisman",1],
["Yawgmoth’s Will",2]

]


maxpoints = 0

for item in canadian_highlander_cards:
    maxpoints = maxpoints + item[1]
deck = []
deckstats = []
cards = open("sampledeck.txt","r")
for card in cards:
    card = card.replace('\n',"")
    if card == "":
        pass
    else:
        copies = int(card.split(' ')[0])
        for copy in range(copies):
            deck.append(card.split(' ',1)[1])

cards.close()
for card in deck:
    detail,found = search(card)
    deckstats.append(Card(found,detail))



driver = webdriver.Chrome()
for card in deckstats:
    if card.found == True:
        #print('scrape %s' %card.name)
        # EDH Scrape
        #edhrec_scrape(card)

        #Highlander Score
        for item in canadian_highlander_cards:
            if card.name.lower() == item[0].lower():
                print('found %s - adding points'%card.name)
                card.highlander_points = card.highlander_points+item[1]
        
        
    else:
        print('skipped %s, unknown card'%card.name)
        pass
driver.close()
driver.quit()

deckscore = 0

for card in deckstats:
    deckscore = deckscore + card.highlander_points
