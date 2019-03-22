#scrape_mars.py to scrape relevant data from mission_to_mars notebook and store in mars_data dict

def scrape():
    # HW10 - Mission to Mars
    #Dependencies
    from bs4 import BeautifulSoup as bs
    from splinter import Browser
    import pandas as pd
    import requests
    import time

    ## Step 1 - Scraping
    ### NASA Mars News
    #Executable Path
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    #Browser visit
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(url)

    #Create BeautifuSoup object
    html = browser.html
    soup = bs(html,'html.parser')

    #Save latest article title and paragraph text into string variables

    #Allow time to avoid error
    time.sleep(2)

    news_title = soup.find('div', class_="content_title").text
    news_p = soup.find('div', class_="article_teaser_body").text

    ### JPL Mars Space Images - Featured Image

    #Visit Mars Featured Image Page

    featured_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(featured_url)

    #Ask browser to click "FULL IMAGE" button

    browser.click_link_by_partial_text('FULL IMAGE')

    #Ask Broswer to click "more info button"

    #Allow time to avoid error
    time.sleep(5)

    browser.click_link_by_partial_text('more info')

    #Create BeautifulSoup object

    featured_html = browser.html
    featured_soup = bs(featured_html,'html.parser')

    #Store url of full size featured image
    featured_image_url ="https://www.jpl.nasa.gov" + featured_soup.find('figure', class_ = "lede").a['href']

    ### Mars Weather

    #Visit Mars Weather Twitter Page

    mars_twitter_url = "https://twitter.com/marswxreport?lang=en"

    browser.visit(mars_twitter_url)

    #Create BeautifulSoup object
    twitter_html = browser.html
    twitter_soup = bs(twitter_html, 'html.parser')

    #Retrive all tweets from timeline

    tweets_all = twitter_soup.find_all\
        ("div", class_ = "tweet")

    #Create mars_weather variable which will contain the text from the Mars Weather twitter reports

    mars_weather = ""


    #Iterate through tweets in timeline

    for tweet in tweets_all:
        
        #If loop found the latest weather report, end for loop
        
        if mars_weather != "":
            break
        
        #Verify the tweet is from the Mars Weather Account
        content = tweet.find("div", class_ = "content")
        header_container = content.find("div", class_ = "stream-item-header")
        anchor = header_container.find("a", class_ = "js-user-profile-link")
        span = anchor.find("span", class_ = "FullNameGroup")
        user_name = span.find("strong", class_ = "fullname").text
        
        if user_name == "Mars Weather":
            
            #Verify the tweet is a weather report
            
            text_container = content.find("div", class_ = "js-tweet-text-container")
            tweet_p = text_container.find("p", class_ = "js-tweet-text")
            
            #Drop Anchor tag if it exists in p element (irrelevant text)
            if tweet_p.find("a", class_ = "twitter-timeline-link"):
                tweet_p.find("a", class_ = "twitter-timeline-link").decompose()
        
            #Store relevant text into tweet_text
            tweet_text = tweet_p.text
            
            #If the tweet is a weather report, store text into mars_weather

            if tweet_text[0:11] == "InSight sol":
                mars_weather = tweet_text


    
    ### Mars Facts


    ### Mars Hemispheres

    #Visit Mars Facts webpage

    facts_url = "https://space-facts.com/mars/"

    tables = pd.read_html(facts_url)

    #Create dataframe

    df  = tables[0]
    df.columns = ['Description', 'Value']
    df.set_index('Description', inplace = True)

    #Create HTML table string

    html_table = df.to_html()
    html_table = html_table.replace('\n', '')

    #Visit USGS AstrogeologyPage

    astrogeology_page_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    browser.visit(astrogeology_page_url)

    #Create Beautiful Soup object
    hemisphere_html = browser.html
    hemisphere_soup = bs(hemisphere_html, 'html.parser')

    #Find sections for all hemispheres
    hemispheres = hemisphere_soup.find_all("div", class_ = "item")

    #Create image urls list
    hemisphere_image_urls = []

    #Iterate through hemispheres 
    for hemisphere in hemispheres:
        #Visit specfic hemisphere page
        base_url = "https://astrogeology.usgs.gov"
        hemisphere_page = base_url + hemisphere.a['href']
        browser.visit(hemisphere_page)
        
        #Create BS object
        sub_html = browser.html
        sub_soup = bs(sub_html, 'html.parser')
        
        #Find hemisphere title
        sub_title_container = sub_soup.find("section", class_ = "block metadata")
        sub_title = sub_title_container.h2.text
        #Remove "Enhanced" from the end
        sub_title_cut = sub_title[:-9]
        
        #Find image url
        sub_image_div = sub_soup.find("div", class_ = "downloads")
        sub_image_ul = sub_image_div.ul
        sub_image_url = sub_image_ul.li.a['href']
        
        #Append list with dictionary
        hemisphere_image_urls.append(
            {'title': sub_title_cut,
            'img_url': sub_image_url
            }
        )

    browser.quit()
    

    mars_data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_facts": html_table,
        "mars_weather": mars_weather,
        "hemisphere_image_urls": hemisphere_image_urls
    }
    
    return mars_data