import time
from utils.logger import CustomLogger
from utils.webhook import send_webhook
import requests
import random
import json

logger = CustomLogger(__name__)

proxy_list = []


def proxy_format():
    try:
        with open("proxy.txt", "r") as file:
            for octet in file:
                octet = octet.strip().split(":")
                proxy_list.append(f"http://{octet[2]}:{octet[3]}@{octet[0]}:{octet[1]}")
    except Exception as e:
        logger.error(e)


def load_previous_data():
    try:
        with open('pinged.json', 'r') as file:
            return json.load(file)['pinged']
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_data(data):
    with open('pinged.json', 'w') as file:
        json.dump({"pinged": data}, file, indent=4)


def fetch_data(url):
    result = []
    page_number = 0
    while url:
        try:
            response = requests.get(url, proxies={"https": random.choice(proxy_list)})

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                result.extend(results)
                pagination = data.get('pagination', {})
                if pagination.get('totalPages', 0) > pagination.get('page', 0):
                    page_number += 1
                    url = f"https://api-sell.wethenew.com/consignment-slots?skip={page_number * 10}&take=100"
                else:
                    url = None
            else:
                logger.error(f"Failed to fetch data")
                url = None
        except requests.RequestException as e:
            logger.error(e)
            url = None

    return result


def main():
    first_iteration = True

    while True:
        all_data = fetch_data("https://api-sell.wethenew.com/consignment-slots?skip=0&take=100")
        previous_data = load_previous_data()

        if all_data:
            if first_iteration:
                save_data(all_data)
                logger.info("Data saved")
                first_iteration = False
            else:
                if previous_data:
                    added_items = [item for item in all_data if item['id'] not in [obj['id'] for obj in previous_data]]
                    deleted_items = [item for item in previous_data if item['id'] not in [obj['id'] for obj in all_data]]

                    for added_item in added_items:
                        logger.info(f"Item added: {added_item['name']}")
                        send_webhook(added_item)
                    for deleted_item in deleted_items:
                        logger.error(f"Item removed: {deleted_item['name']}")


                    for current_item in all_data:
                        previous_item = next((prev_item for prev_item in previous_data if prev_item['id'] == current_item['id']), None)
                        if previous_item:
                            if len(previous_item['sizes']) < len(current_item['sizes']):
                                logger.debug(f"Size added: {previous_item['name']}")
                                send_webhook(current_item)
                            elif len(previous_item['sizes']) > len(current_item['sizes']):
                                logger.warning(f"Sizes removed: {current_item['name']}")

                    save_data(all_data)

                else:
                    logger.debug("No changes")

        else:
            logger.warning("Error fetching data")

        time.sleep(10)


if __name__ == '__main__':
    proxy_format()
    main()
