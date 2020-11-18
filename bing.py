#!/bin/env python

# A python script which makes numSearches number of searches to your Bing Account
# without you having to lift a finger :) Might take an argument as to number of
# searches in the future. Who knows?

#Type this into Terminal: 
#python3 bing.py cgarren18@icloud.com Cg2018066

import time
import os
import random
import argparse
import getpath

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentExeption
from selenium.webdriver.common.action_chains import ActionChains
# Want to replace the time.sleep calls with webdriverwait, but not yet
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
from BingSelectors import xpath

numSearches = 60 
numMobileSearches = 22
authPause = 10
searchPause = 5

parser = argparse.ArgumentParser()
parser.add_argument("uname")
parser.add_argument("pswd")
args = parser.parse_args()
username = args.uname
password = args.pswd

starturl = "https://account.microsoft.com/rewards/dashboard"
directory = getpath.get_script_dir()

# should be a config option to set this
userAgentString = "Mozilla/5.0 (Android 5.0.1; Mobile; rv:58.0) Gecko/58.0 Firefox/58.0"


def get_random_queries(numQueries):
    with open(os.path.join(directory, "queries"), "r") as queryTxtfile:
        allWords = list(queryTxtfile)

    queries = set()
    while len(queries) < numQueries:
        queries.add(random.choice(allWords).rstrip())
    return queries

# Make a "Driver" class to fit these into
def send(xpath, value):
    try:
        elem = driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        print("Couldn't find element specified by xpath: {x}".format(x=xpath))
    elem.send_keys(value)

def click(path):
    try:
        elem = driver.find_element_by_xpath(path)
        elem.click()
    except NoSuchElementException:
        print("Couldn't find element specified by xpath: {x}".format(x=path))
        try:
        	elem = driver.find_element_by_xpath(xpath['searchButtonMobile'])
        	elem.click()
        except NoSuchElementException:
        	print("Couldn't find element specified by xpath: {x}".format(x=path))
        	elem = driver.find_element_by_xpath(xpath['searchButton'])
        	elem.click()

def click_CSS(selector):
    try:
        elem = driver.find_element_by_css_selector(selector)
    except NoSuchElementException:
        print("Couldn't find element specified by css selector: {x}".format(x=selector))
    elem.click()

def clear(xpath):
    try:
        elem = driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        print("Couldn't find element specified by xpath: {x}".format(x=xpath))
    elem.clear()

def exists(xpath):
    try:
        _ = driver.find_element_by_xpath(xpath)
        return True
    except NoSuchElementException:
        print("Couldn't find element(s) specified by xpath: {x}".format(x=xpath))
        return False

# Authenticate Bing Rewards Account
def login():
	print ('Maximizing window...')
	driver.maximize_window()
	driver.get(starturl)
	print ('Logging in...')
	click(xpath['signInLink'])
	time.sleep(authPause/2)
	send(xpath['usernameBox'], username)
	click(xpath['submit'])
	time.sleep(authPause/4)
	send(xpath['pswdBox'], password)
	click(xpath['submit'])
	time.sleep(authPause)

def solve_quiz(numPoints):
    numQuestions = numPoints//10
    draggable = True if exists(xpath['draggableQuizBox']) else False
    for _ in range(0,numQuestions):
        triesPerQuestion = 8 if draggable else 4
        for j in range(0,triesPerQuestion):
            quizOptionElements = get_quiz_option_elements()
            if quizOptionElements[j].is_displayed():
                if draggable:
                    drag_and_drop_elements(quizOptionElements)
                else:
                    quizOptionElements[j].click()
                time.sleep(searchPause)
            else:
                return

def get_quiz_option_elements():
    elements = []
    for i in range(0,4):
        key = 'quizOption'+str(i)
        elements.append(driver.find_element_by_xpath(xpath[key]))
    return elements

def drag_and_drop_elements(elements):
    allAnswers = driver.find_elements_by_xpath(xpath['allDragAnswers'])

    try:
        wrongAnswers = driver.find_elements_by_xpath(xpath['wrongDragAnswers'])
    except NoSuchElementException:
        wrongAnswers = []
    
    try:
        rightAnswers = driver.find_elements_by_xpath(xpath['rightDragAnswers'])
    except NoSuchElementException:
        rightAnswers = []
        
    unmarkedAnswers = list((set(wrongAnswers) | set(rightAnswers)) ^ set(allAnswers))
    #                                         ^ union              ^ symmetric diff

    if len(unmarkedAnswers) > 1:
        elems = random.sample(unmarkedAnswers,2)
        elemToDrag = elems[0]
        elemToDropOn = elems[1]
    elif len(unmarkedAnswers) == 1:
        elemToDrag = unmarkedAnswers[0]
        elemToDropOn = random.choice(wrongAnswers)
    else:
        elems = random.sample(wrongAnswers,2)
        elemToDrag = elems[0]
        elemToDropOn = elems[1]

    ActionChains(driver).drag_and_drop(elemToDrag, elemToDropOn).perform()

def get_offer_points():
	print ("0")
	allOfferCardTitles = driver.find_elements_by_xpath(xpath['rewardsHomeCardTitle'])
	allOfferCardStatuses = driver.find_elements_by_xpath(xpath['rewardsHomeCardCheckmarkOrChevron'])
	print (allOfferCardStatuses)
	allVisibleOfferCardStatuses = [x for x in allOfferCardStatuses if x.is_displayed()]

	allOfferCardPoints = driver.find_elements_by_xpath(xpath['rewardsHomeCardPoints'])
	allVisibleOfferCardPoints = [x for x in allOfferCardPoints if x.is_displayed()]

	for i in range(0,len(allVisibleOfferCardStatuses)):
		elem = allVisibleOfferCardStatuses[i]
		print ("1")
		if "mee-icon-ChevronRight" in elem.get_attribute("class"):
			titleElem = allOfferCardTitles[i]
			print ("2")

			# Got to clean this up
			if "Quiz" in titleElem.text or "quiz" in titleElem.text:
				print ("3")
				numPointsStr = allVisibleOfferCardPoints[i].text.replace(' POINTS','')
				elem.click()
				time.sleep(searchPause)
				currTab = driver.window_handles[0]
				newTab = driver.window_handles[-1]
				driver.switch_to_window(newTab)
				click(xpath['startQuizButton'])
				solve_quiz(int(numPointsStr))
				driver.close()
				driver.switch_to_window(currTab)
				get_offer_points()
				return
			else:
				print ("4")
				elem.click()
				time.sleep(searchPause)
				currTab = driver.window_handles[0]
				newTab = driver.window_handles[-1]
				driver.switch_to_window(newTab)
				driver.close()
				driver.switch_to_window(currTab)
				return

def isAlertPresent():
    try:
        driver.switch_to.alert()
        return True
    except:
        return False

def visit_PC_search_page():
	print ('Going to bing...')
	home_tab = driver.window_handles[0]
	
	#New Tab
	driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')

	driver.switch_to.window(driver.window_handles[-1])

	driver.get('https://www.bing.com/')
	click(xpath["searchLink"])
	time.sleep(authPause/2)

    # switches focus to the new tab where the search window has opened up
    #newTab = driver.window_handles[-1]
    #driver.switch_to.window(newTab)

def visit_mobile_search_page():
    # click(xpath['searchLinkMobile'])
    driver.get('https://www.bing.com/')
    click(xpath['searchLink'])    
    time.sleep(authPause/2)

def do_searches(numSearches, searchQuries):
    for _ in range(0, numSearches):
        clear(xpath['search'])
        search = xpath['search']
        querie = searchQuries.pop()
        send(search, querie)
        click(xpath['searchButton'])
        print ('Searched for:', querie)
        time.sleep(searchPause)

def do_mobile_searches(numSearches, searchQuries):
    x = 0
    for _ in range(0, numSearches):
    	present = isAlertPresent()
    	if present == True:
    		alert = driver.switchTo().alert()
    		alert_text = alert.getText()
    		print ("Accepting alert that says: ", alert_text)
    		alert.accept()
    	clear(xpath['search'])
    	search = xpath['search']
    	querie = searchQuries.pop()
    	send(search, querie)
    	if x <= 1:
    		click(xpath['searchButtonMobile'])
    		 #print('Clicked mobile button')
    		 #click(xpath['searchButtonMobile'])
    	else:
    		#print ('Alert present?', present)
    		click(xpath['searchButton'])
    	x += 1
    	#print (x)
    	print ('Searched for:', querie)
    	time.sleep(searchPause)

# Get search terms
terms = get_random_queries(numSearches+numMobileSearches)

# Perform PC searches
driver = webdriver.Firefox()
login()
get_offer_points()
visit_PC_search_page()
do_searches(numSearches, terms)
#Close Tab
#driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')
print('Switching to mobile searches...')
#currTab = driver.window_handles[0]
#driver.switch_to.window(currTab)
driver.quit()
#driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')

# Perform Mobile searches
profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", userAgentString)
driver = webdriver.Firefox(profile)
login()
visit_mobile_search_page()
do_mobile_searches(numMobileSearches, terms)
driver.quit()

