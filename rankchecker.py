from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import re
import time

driver = None

while driver is None:
    requestedBrowser = input("Run script in Chrome or Firefox? ")

    match requestedBrowser.lower().strip():
        case "chrome":
            driver = webdriver.Chrome()
        case "firefox":
            driver = webdriver.Firefox()
        case _:
            print("Please choose a supported browser.")

#search function
def search(url, searchPhrase):
    driver.get(url)
    entryField = driver.find_element(By.NAME, "q")
    entryField.clear()
    entryField.send_keys(searchPhrase)
    entryField.submit()

requestedSearchEngines = input("Enter desired search engines, separated by commas if multiple (Currently supported: Google, Bing, DuckDuckGo) : ")
requestedSearchPhrases = input("Enter desired search terms or phrases, separated by commas if multiple : ")
requestedSearchDomain = input("Enter domain to match : ")

charactersToBeCleared = ["http://", "https://", "www."]

for character in charactersToBeCleared:

    if requestedSearchDomain.find(character) != -1:
        requestedSearchDomain = requestedSearchDomain.replace(character, "")

searchEngines = requestedSearchEngines.split(",")
searchPhrases = requestedSearchPhrases.split(",")

# strip leading and trailing whitespaces
for x in range(len(searchPhrases)):
    searchPhrases[x] = searchPhrases[x].strip()

results = {}

for searchEngine in searchEngines:

    match searchEngine.lower().strip():
        case 'google':

            googleResults = []

            for searchPhrase in searchPhrases:

                search("https://www.google.com/", searchPhrase)

                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "cite"))
                )

                matchFound = False

                while not matchFound:

                    time.sleep(3)

                    resultsURLs = driver.find_elements(By.TAG_NAME, "cite")

                    urlCounter = 1

                    for url in resultsURLs:

                        if re.search(requestedSearchDomain, url.text):
                            googleResults.append({searchPhrase: urlCounter})
                            matchFound = True
                            break
                        
                        if url.text:
                            urlCounter += 1

                    time.sleep(3)

                    if not matchFound:

                        heightBeforeScroll = driver.execute_script("return document.body.scrollHeight")

                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                        time.sleep(3)

                        heightAfterScroll = driver.execute_script("return document.body.scrollHeight")

                        if heightBeforeScroll == heightAfterScroll:
                            googleResults.append({searchPhrase: "not found"})
                            matchFound = True
   
            results["Google"] = googleResults

        case 'bing':

            bingResults = []

            for searchPhrase in searchPhrases:

                search("https://www.bing.com/", searchPhrase)

                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "cite"))
                )
                
                urlCounter = 1

                matchFound = False

                while not matchFound:

                    resultsURLs = driver.find_elements(By.XPATH, "//div[@class='b_attribution']/cite")

                    for url in resultsURLs:

                        if re.search(requestedSearchDomain, url.text):
                            bingResults.append({searchPhrase: urlCounter})
                            matchFound = True
                            break
                            
                        urlCounter += 1

                    time.sleep(3)

                    if not matchFound:

                        nextButton = driver.find_element(By.XPATH, '//*[@title="Next page"]')
                        nextButton.click()

            results["Bing"] = bingResults

        case 'duckduckgo':

            ddgResults = []

            for searchPhrase in searchPhrases:

                search("https://www.duckduckgo.com/", searchPhrase)

                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//li[@data-layout='organic']/article/div/div/a"))
                )

                matchFound = False

                while not matchFound:

                    urlCounter = 1

                    resultsURLs = driver.find_elements(By.XPATH, "//li[@data-layout='organic']/article/div/div/a")

                    for url in resultsURLs:

                        if re.search(requestedSearchDomain, url.text):
                            ddgResults.append({searchPhrase: urlCounter})
                            matchFound = True
                            break
                            
                        urlCounter += 1

                    time.sleep(3)

                    if not matchFound:

                        nextButton = driver.find_element(By.XPATH, '//*[@id="more-results"]')
                        nextButton.click()

            results["DuckDuckGo"] = ddgResults

        case _:
            print('Not a valid selection.')

fileName = str(time.time()).replace(".", "")+".csv"

with open(fileName, 'w', newline='') as file:
    writer = csv.writer(file)

    for result in results:
        writer.writerow([result])

        searchTermResults = results[result]
        searchTermCounter = 0

        for searchTermResult in searchTermResults:

            writer.writerow([searchPhrases[searchTermCounter], searchTermResult[searchPhrases[searchTermCounter]]])

            searchTermCounter += 1

driver.quit()