import itertools
import random
import time
import uuid
import requests

ENDPOINT="localhost:2113"
STREAM="commerce"
MAX_PRODUCT_COUNT=10

def select_user():
    return random.randint(1230,1240)

def select_product():
    return random.randint(9870,9890)

def select_products():
    return set([select_product() for i in range(MAX_PRODUCT_COUNT)])

def add_products_to_cart(products):
    return random.sample(products, random.randint(1, 3))

def remove_products_from_cart(products):
    return random.sample(products, 1)

def event_visit_product_page(user_id, product_id):
    return {'data': {'UserId': user_id,
                     'ProductId': product_id},
            'eventType': 'VisitedProductPage',
            'eventId': str(uuid.uuid4())}

def event_add_product_to_cart(user_id, product_id):
    return {'data': {'UserId': user_id,
                     'ProductId': product_id},
            'eventType': 'AddedToCart',
            'eventId': str(uuid.uuid4())}

def event_remove_product_from_cart(user_id, product_id):
    return {'data': {'UserId': user_id,
                     'ProductId': product_id},
            'eventType': 'RemovedFromCart',
            'eventId': str(uuid.uuid4())}

def generate_events():
    user_id = select_user()
    products = select_products()

    products_adds = add_products_to_cart(products)
    products_removes = remove_products_from_cart(products)

    product_visits = [(event_visit_product_page(user_id, product_id))
                      for product_id in products]
    cart_adds = [(event_add_product_to_cart(user_id, product_id))
                 for product_id in products_adds]
    cart_removes = [(event_remove_product_from_cart(user_id, product_id))
                    for product_id in products_removes]

    return product_visits + cart_adds + cart_removes

def push(event):
    print('==> ', event)
    r = requests.post('http://' + ENDPOINT + '/streams/' + STREAM,
                      json=event,
                      headers={'Content-Type': 'application/vnd.eventstore.events+json'})
    print('<== ', r.status_code, r.reason)
    print()

if __name__ == "__main__":
    while True:
        push(generate_events())
        time.sleep(1)
