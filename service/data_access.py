import requests
import logging
from sesamutils import sesam_logger
import json

# logger = logging.getLogger(f"graphql.{__name__}")
logger = sesam_logger("GraphQL")


class DataAccess:

    def __init__(self, config):
        self.session = None
        self.auth_header = None
        self.config = config

    def __get_all_entities(self, url, query):
        logger.info('Fetching entities')
        url = self.config.baseurl + url
        logger.debug("url: " + url)
        req = self.request("POST", url, query)
        if not req.ok:
            logger.debug(req)
            logger.info('request not ok')
        else:
            logger.debug("req.ok in __get_all_entities")
            res = req.json()

            yield res

    def get_entities(self, url, query):
        logger.info("Getting all entities")
        return self.__get_all_entities(url, query)

    def get_token(self):
        payload = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": self.config.grant_type,
            "resource": self.config.resource
        }
        logger.info("Acquiring new access token")
        try:
            resp = requests.post(url=self.config.token_url, data=payload)
            if not resp.ok:
                logger.error(f"Access token request failed. Error: {resp.content}")
                raise
        except Exception as e:
            logger.error(f"Failed to talk to token service. Error: {e}")
            raise
        access_token = resp.json().get("access_token")
        self.auth_header = {"Content-type": "application/json", "Authorization": "Bearer " + access_token}

    def request(self, method, url, query, **kwargs):
        if not self.session:
            self.session = requests.Session()
            self.get_token()

        if "headers" in kwargs:
            headers = {**kwargs["headers"], **self.auth_header}
            kwargs.pop("headers")
            logger.debug("headers in kwargs")
        else:
            logger.debug("headers not in kwargs")
            headers = self.auth_header

        if "json" in kwargs:
            headers = {**headers, "Content-Type": "application/json"}
            logger.debug("json in kwargs")

        logger.debug("headers before req build: " + str(headers))
        logger.debug("query before req build: " + str(query))

        req = requests.Request(method, url, headers=headers, data=query, **kwargs)
        logger.debug("got past requests.Request")
        try:
            resp = self.session.send(req.prepare())
        except Exception as e:
            logger.error(f"Failed to send request. Error: {e}")
            raise
        logger.debug("got past session.send(req.prepare)")
        if resp.status_code == 401:
            logger.warning("Received status 401. Requesting new access token.")
            self.get_token()
            resp = self.session.send(req.prepare())
        logger.debug("got to end of request method")
        return resp
