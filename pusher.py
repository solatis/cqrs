import itertools
import random
import time
import uuid
import requests
import numpy

ENDPOINT="localhost:2113"
STREAM="commerce"
SPEED=25
USERS=100
PRODUCTS=10000

events = ["VisitedProductPage",
          "AddedToCart",
          "RemovedFromCart",
          "CheckedOut",
          "SentBack"]

transitionMatrix = [[0, 1],
                    [1, 0, 2, 3, -1],
                    [1, 0, 3, -1],
                    [0, 4, -1],
                    [0, -1]]

transitionProbabilities = [[0.7,0.3],
                           [0.1,0.3,0.1,0.4,0.1],
                           [0.5, 0.2, 0.2, 0.1],
                           [0.2, 0.1, 0.7],
                           [0.25, 0.75]]

def select_user():
    return random.randint(0,USERS)

def select_product():
    return random.randint(0,PRODUCTS)


def transition_generator(cur = 0, product_id = select_product()):
    while True:
        cur = numpy.random.choice(transitionMatrix[cur],replace=True,p=transitionProbabilities[cur])

        if cur == -1:
            return

        if cur == 0:
            # Visit new product page
            product_id = select_product()

        yield events[cur], product_id

def transitions():
    gen = transition_generator()

    xs = []

    while True:
        try:
            event, product_id = next(gen)
        except StopIteration:
            break

        xs.append((event, product_id))

    return xs

def generate_events():
    user_id = select_user()


    events = []

    for event, product_id in transitions():
        events.append({'data': {'UserId': user_id,
                                'ProductId': product_id,
                                'Timestamp': int(time.time())
                               },
                       'eventType': event,
                       'eventId': str(uuid.uuid4())})

    return events

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
        time.sleep(random.randint(1,10)/SPEED)
