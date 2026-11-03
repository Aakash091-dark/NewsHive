import logging
import time
from tor.tor import authenticate_controller, change_tor_ip

class TorSessionManager:
    def __init__(self):
        self.controller = None
        self.current_ip = None
        self.session_active = False
        self.last_ip_change_time = None

    def _ensure_controller(self):
        if self.controller is None:
            try:
                self.controller = authenticate_controller()
            except Exception as e:
                logging.error(f"Failed to authenticate Tor controller: {e}")
                raise

    def start_session(self):
        if not self.session_active:
            try:
                self._ensure_controller()
                self.current_ip = change_tor_ip(self.controller)
                if self.current_ip:
                    self.session_active = True
                    self.last_ip_change_time = time.time()
                    logging.info(f"Tor session started with IP: {self.current_ip}")
                else:
                    logging.error("Failed to get a new Tor IP. Session not started.")
                    self.session_active = False
            except Exception as e:
                logging.error(f"Error starting Tor session: {e}")
                self.session_active = False
        return self.session_active

    def get_session(self):
        if not self.session_active:
            self.start_session()
        
        if self.session_active and (time.time() - self.last_ip_change_time) > 30 * 60:
            logging.info("30 minutes have passed. Renewing Tor IP.")
            self.renew_ip()
            
        return self.controller

    def renew_ip(self):
        if not self.session_active:
            logging.warning("Cannot renew IP. Session not active.")
            return self.start_session()

        try:
            self.current_ip = change_tor_ip(self.controller)
            if self.current_ip:
                self.last_ip_change_time = time.time()
                logging.info(f"Tor IP renewed. New IP: {self.current_ip}")
                return True
            else:
                logging.error("Failed to get a new Tor IP during renewal.")
                return False
        except Exception as e:
            logging.error(f"Error renewing Tor IP: {e}")
            return False

    def close_session(self):
        if self.controller:
            self.controller.close()
            self.controller = None
        self.session_active = False
        logging.info("Tor session closed.")

tor_session_manager = TorSessionManager()
