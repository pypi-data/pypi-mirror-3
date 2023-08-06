import mechanize
import BeautifulSoup
import cookielib
import re
import time
import logging
from urlparse import urlparse
from cgi import parse_qs
from urllib import quote
from datetime import date 
# The URL to this service
# WW Mobile URL, note bhjs=0 at the end to say we DON'T have JavaScript 
base_url = 'http://mobile.weightwatchers.com'

logger = logging.getLogger('WWScraper')

class WWScrape():
    """
    Class for scraping and operating the WeightWatchers mobile website 
    """
    def __init__(self):
        # Create our cookie jar and browser instance
        self.cj = cookielib.LWPCookieJar()
        self.browser = mechanize.Browser()
        self.browser.set_cookiejar(self.cj)
        self.logged_in = False
        
    def connect(self,username,password):
        """
        Connect and login to the WW Mobile website
        """
        login_url = base_url + '/mobile/index.aspx?bhjs=0'
        self.browser.open(login_url)
        self.browser.select_form(nr=0)

        logger.info("Logging in using %s:%s" % (username,password))
        self.browser['txtUsername'] = username
        self.browser['txtPassword'] = password
        self.browser.submit()

        logger.info("Logged In")
        #TODO, check if we actually got logged in

    def disconnect(self):
        # Get to a known state
        url = base_url + '/mobile/login/Logout.aspx'
        self.browser.open(url)
                
    def food_search(self,lookup_string,max_results=None):
        """
        Runs a search against the WW Database for a food
        You can provide a max_results, this helps you avoid issues where you
        accidentially grab like 3000 records.

        Returns a list of tuples (Food Name, Food ID#, Serving, Pts Value)
        """

        food_result_list = []

        # Get to a known state
        search_url = base_url + '/mobile/index.aspx'
        self.browser.open(search_url)
   
        # Fill out the search form (only one on this page)
        self.browser.select_form(nr=0)
        self.browser['ctl01$txtSearchKeyword']=lookup_string

        #Pull and parse our results
        results = self.browser.submit()

        page_id = 0
        total_grabbed = 0
        total_ignored = 0

        soup = BeautifulSoup.BeautifulSoup(results.read())
        total_results = soup.findAll(text=re.compile('results of'))
        total_found = int(total_results[0].split()[-1])
     
        if max_results:
            total_found = min((total_found,max_results))
 
        while total_grabbed  + total_ignored < total_found:
 
            if page_id != 0:
                links = soup.findAll('a')
                for link in links:
                    if 'Next' in link.contents[0]:
                        # We have to do some munging here with the URL
                        # since we filled the form in before, and WW
                        # doesn't seem to properly re-encode it with the next
                        # link
                        next_url = base_url + link['href']
                        encoded_url = next_url.replace(lookup_string,quote(lookup_string))
                        next_page = self.browser.open(encoded_url)
                        soup = BeautifulSoup.BeautifulSoup(next_page.read())
                        time.sleep(5)

            items = soup.findAll('div', 
                     id=re.compile('^ucFoodSearchResults_repFoodList_trItemRow_.*'))

            for item in items:
                if total_grabbed >= total_found:
                    break 

                # Grab all the info about this item
                description = item.find('span',{"class":"left"})
                food_serving = description.contents[-1][3:].rstrip()
                points_field = item.find('span', id=re.compile('^ucFoodSearchResults_repFoodList_lblPointsValue_.*'))
                points_val = None
                if points_field:
                    points_val = int(points_field.contents[0])
                else:
                    total_ignored += 1
                    continue

                # Food name is wrapped in a link, 
                food_name = description.find('a').contents[0].lstrip().rstrip()

                # Food ID is encoded into the HREF link, if there's no ID ecnoded though, it's historic
                food_url = description.find('a')['href']
                try:
                    food_id = parse_qs(urlparse(food_url)[4])['id'][0] 
                except KeyError:
                    # This food doesn't have an ID, probably a historic food.
                    # WW seems to put these at the end of the 'valid' list, so we can toss out everything after this
                    total_ignored = total_found - total_grabbed
                    continue

                food_result_list.append((food_name,food_id,food_serving,points_val))
                total_grabbed += 1
                 

            logger.debug("Page ID: %s - Recored: %s Ignored: %s of %s" % (
                            page_id, total_grabbed, total_ignored, total_found))

            page_id += 1
      
        return food_result_list 

    def data_for_date(self,lookup_date):
        """
        Given a datetime.date object, will grab the points data from that 
        given day
        """
        date_lookup_url = base_url + '/mobile/plan/Index.aspx?CurrentDate=%s'

        # Convert the date into a friendly format for WW site
        date_text = lookup_date.strftime('%m/%d/%Y')
        day_page = self.browser.open(date_lookup_url % date_text)

        # Parse the page to get our points info
	soup = BeautifulSoup.BeautifulSoup(day_page.read())

        #Extract daily points allowance, points used, bonus points availi
        points_used = int(soup.find("span", {'id':'lblDailyUsedValue'}).contents[0])
        points_remain = int(soup.find("span", {'id':'lblDailyRemainingValue'}).contents[0])
        flex_remain = int(soup.find("span", {'id':'lblWeeklyRemainigFlexValue'}).contents[0])
        activity_earned = int(soup.find("span", {'id':'lblActivityEarnedFlexValue'}).contents[0])
        activity_remain = int(soup.find("span", {'id':'lblActivityRemainigValue'}).contents[0])
        
        data = {}
        data['summary'] = (points_used,points_remain,
                           flex_remain,activity_earned,
                           activity_remain)
            

        food_data_blocks = soup.findAll("div", "col-title")
 
        for food_data in food_data_blocks:
            # Determine the categorm (Morning, MidDay, Evening, Snacks)
            points_category = food_data.findAll('b')[-1].contents[0]

            # If we haven't tracked items, we just return None for the category
            foods = food_data.nextSibling
            if 'No items' in foods:
                data[points_category] = None
                continue
           
            # Actually process any foods that may be there 
            food_list = []
            while foods != None: 
                if isinstance(foods,BeautifulSoup.Tag):   
                    items = foods.findAll('div') 

                    # Handle an edge case where we run out of items
                    if len(items) == 0: 
                        foods=foods.nextSibling
                        continue 

                    # Progperly get our activity description info
                    if 'Activity' in points_category:
                        activity_desc = items[1].next
                        food_desc = activity_desc.contents[0]
                    else:
                        food_desc = items[5].contents[0]         

                    # We have to hunt for the actual points value, since there 
                    # can be a plethora of icons/etc...
                    for section in items[6:]:
                        pts = section.contents[0].lstrip().rstrip()
                        if pts != '':
                            food_points = int(pts)
                            break
                    
                    # add our item to the foods list 
                    food_list.append((decode(food_desc),food_points))

                # move onto the next item in the foods 
                foods = foods.nextSibling

            data[points_category] = food_list

        return data       
