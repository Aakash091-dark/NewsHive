import time
import logging
from stem import Signal
from stem.control import Controller
import requests

CONTROL_HOST = "127.0.0.1"
CONTROL_PORT = 9051
CONTROL_PASSWORD = "StrongCtrlPass123"
SOCKS_HOST = "127.0.0.1"
SOCKS_PORT = 9050

SLEEP_BETWEEN_ACTIONS_MIN = 5
SLEEP_BETWEEN_ACTIONS_MAX = 10

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def authenticate_controller(host=CONTROL_HOST, port=CONTROL_PORT, password=CONTROL_PASSWORD):
    controller = Controller.from_port(address=host, port=port)
    controller.authenticate(password=password)
    logging.info("Authenticated to Tor control port")
    return controller


def change_tor_ip(controller):
    controller.signal(Signal.NEWNYM)
    logging.info("Requested new Tor identity")
    time.sleep(10)

    try:
        proxies = {
            "http": f"socks5h://{SOCKS_HOST}:{SOCKS_PORT}",
            "https": f"socks5h://{SOCKS_HOST}:{SOCKS_PORT}"
        }
        r = requests.get("https://api64.ipify.org?format=json", proxies=proxies, timeout=10)
        ip = r.json().get("ip")
        logging.info("Current Tor exit IP: %s", ip)
        return ip
    except Exception as e:
        logging.warning("Could not fetch exit IP: %s", e)
        return None
