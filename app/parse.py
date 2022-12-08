import csv

from dataclasses import dataclass, fields, astuple
from time import sleep

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int


_driver: WebDriver | None = None
HEADERS = [field.name for field in fields(Product)]
BASE_URL = "https://webscraper.io/test-sites/e-commerce/more/"
URLS_FOR_PARSING = {
    "home": BASE_URL,
    "computers": "computers",
    "laptops": "computers/laptops",
    "tablets": "computers/tablets",
    "phones": "phones",
    "touch": "phones/touch",
}


def get_driver() -> WebDriver:
    return _driver


def set_driver(new_driver: WebDriver) -> None:
    global _driver
    _driver = new_driver


def write_to_csv(path_to_csv: str, products: [Product]) -> None:
    with open(path_to_csv, "w", encoding="UTF-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS)
        writer.writerows([astuple(product) for product in products])


def accept_cookies() -> None:
    try:
        get_driver().find_element(By.CLASS_NAME, "acceptCookies").click()
    except NoSuchElementException:
        pass


def paginating() -> None:
    try:
        more_btn = get_driver().find_element(By.CLASS_NAME, "ecomerce-items-scroll-more")
    except NoSuchElementException:
        return

    while True:
        if more_btn.is_displayed():
            more_btn.click()
            sleep(0.1)
        else:
            break


def get_product_info(card) -> Product:
    title = card.find_element(By.CSS_SELECTOR, ".caption .title").get_attribute("title")
    price = float(card.find_element(By.CSS_SELECTOR, ".caption .price").text.replace("$", ""))
    description = card.find_element(By.CSS_SELECTOR, ".description").text
    num_of_reviews = int(card.find_element(By.CSS_SELECTOR, ".ratings p").text.split()[0])
    rating = len(card.find_elements(By.CSS_SELECTOR, ".ratings .glyphicon-star"))

    return Product(
        title=title,
        price=price,
        description=description,
        num_of_reviews=num_of_reviews,
        rating=rating,
    )


def get_all_products() -> None:
    with webdriver.Chrome() as new_driver:
        set_driver(new_driver)

        for category_name, url in URLS_FOR_PARSING.items():
            get_driver().get(BASE_URL + url)
            accept_cookies()
            paginating()

            products = []
            for card in get_driver().find_elements(By.CLASS_NAME, "thumbnail"):
                products.append(get_product_info(card))

            write_to_csv(f"{category_name}.csv", products)


if __name__ == "__main__":
    get_all_products()
