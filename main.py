import argparse
import os
import json
import requests
from time import sleep
from influxdb import InfluxDBClient

def request(url):
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        print("Error getting light status: {0}".format(response.status_code))
        return None

def get_light_status(hue_user, hue_address, interval, db_host, db_port, db_name):

    db_client = InfluxDBClient(host=db_host, port=db_port, database=db_name)
    db_client.create_database(db_name)

    print("Getting light status from {0} with user {1} and sending to {2}:{3} every {4} seconds".format(hue_address, hue_user, db_host, db_port, interval))
    url = "http://{0}/api/{1}".format(hue_address, hue_user)

    ok = True
    while(ok):
        response = request(url)
        metrics = parse_json(response)
        if metrics is not None:
            db_client.write_points(metrics)
        else:
            print('unexpected json result')
            print(response)
        sleep(interval)

def parse_json(response):
    if 'lights' not in response:
        return None
    lights = response['lights']
    metrics = []
    for (light_name, light) in lights.items():
        if 'name' not in light:
            return None
        if 'state' not in light:
            return None
        state = light['state']
        if 'on' not in state:
            return None
        if 'bri' not in state:
            return None
        metrics.append(
            {
                'measurement': 'light',
                'tags': {
                    'name': light['name']
                },
                'fields': {
                    'state': state['on'],
                    'brightness': state['bri'] if state['on'] else 0,
                }
            }
        )
    return metrics


def parse_args():
    parser = argparse.ArgumentParser(description='Light Reporter')
    parser.add_argument('--hue_address', default=os.environ.get('HUE', '192.168.1.5'))
    parser.add_argument('--user', default=os.environ.get('USER', ''))
    parser.add_argument('--interval', type=int, default=int(os.environ.get('INTERVAL', 60)))
    parser.add_argument('--host', default=os.environ.get('HOST', '192.168.1.4'))
    parser.add_argument('--port', default=os.environ.get('PORT', '8086'))
    parser.add_argument('--db', default=os.environ.get('DB_NAME', 'stats'))

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    get_light_status(hue_user=args.user, hue_address=args.hue_address, interval=args.interval, db_host=args.host, db_port=args.port, db_name=args.db)
