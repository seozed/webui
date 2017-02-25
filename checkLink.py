import time
import requests
import settings
from database import get_mongodb
from threading import Thread
from bs4 import BeautifulSoup
import logging


db = get_mongodb()
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                    )


def get_data(item):

    new_item = dict.copy(item)
    url = item['link']
    logging.info("start check {}".format(url))
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find('title')

        if title:
            new_item['title'] = title.text
        if response.status_code != 200 or '已被删除' in response.text:
            new_item['status'] = False
        else:
            new_item['status'] = True

        db[settings.MONGODB_COLLECTION].update(item, new_item)

    except Exception as e:
        print(e)

    else:
        logging.info("status code: {1} {0}".format(url, response.status_code))

if __name__ == '__main__':

    while 1:
        for item in db[settings.MONGODB_COLLECTION].find({'status': {'$ne': False}}):
            t = Thread(target=get_data, args=(item,))
            t.start()

        time.sleep(settings.CHECK_TIMEOUT)