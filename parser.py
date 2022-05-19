import time
import json
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from date_formatter import date_formatter
import requests
#options = Options()
#options.add_argument("--headless")
#browser = webdriver.Firefox()


def get_articles_html(url):
    html = requests.get(url).text
    #if browser.current_url != url:
     #   browser.find_element_by_class_name("CheckboxCaptcha-Button").click()
      #  time.sleep(3)
    soup = BeautifulSoup(html, "lxml")

    articles = soup.find_all("div", class_="mg-grid__col mg-grid__col_xs_4")
    return articles


def parse_articles(articles):
    result = []
    for article in articles:
        try:
            title = article.find("a", class_="mg-card__link").text.replace("\xa0", " ")
            insider = article.find("a", class_="mg-card__source-link").text
            date = article.find("span", class_="mg-card-source__time").text
            link_to_yandex = article.find("a", class_="mg-card__link").attrs["href"]

            html = requests.get(link_to_yandex).text
            '''requests.
            if browser.current_url != link_to_yandex:
                browser.find_element_by_class_name("CheckboxCaptcha-Button").click()
                time.sleep(5)'''

            link = BeautifulSoup(html, 'lxml').find("a", class_="mg-story__title-link").attrs['href']
            image = re.search("(?P<url>https?://[^\s]+)",
                              article.find("div", class_="mg-card__media-block mg-card__media-block_type_image").attrs[
                                  "style"]).group("url")[0:-1]
        except:
            continue

        result.append({"title": title, "link": link, "image": image, "date": date_formatter(date).__str__(), "insider": insider})
    return result


def main(file):
    urls = ["https://yandex.ru/news/rubric/koronavirus", "https://yandex.ru/news",
            "https://yandex.ru/news/region/chelyabinsk",
            "https://yandex.ru/news/rubric/politics", "https://yandex.ru/news/rubric/society",
            "https://yandex.ru/news/rubric/business",
            "https://yandex.ru/news/rubric/world", "https://yandex.ru/sport", "https://yandex.ru/news/rubric/incident",
            "https://yandex.ru/news/rubric/culture", "https://yandex.ru/news/rubric/computers",
            "https://yandex.ru/news/rubric/science", "https://yandex.ru/news/rubric/auto"]
    for url in urls:

        articles_html = get_articles_html(url)
        articles = parse_articles(articles_html)

        with open(file,'a') as f:
            f.writelines(json.dumps(articles))


main("articles.txt")
#browser.quit()
