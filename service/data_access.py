import requests
import logging

logger = logging.getLogger(f"GraphQL.{__name__}")


class DataAccess:

    def __init__(self, config):
        self.session = None
        self.auth_header = None
        self.config = config

    def __get_all_entities(self, url, query):
        url = self.config.baseurl + url
        logger.debug("full url: " + url)
        req = self.request("POST", url, query)
        if not req.ok:
            logger.info('Request not ok')
        else:
            res = req.json()
            logger.debug("request ok. yielding result.")
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
            logger.debug("found headers in kwargs")
        else:
            logger.debug("no headers in kwargs")
            headers = self.auth_header

        if "json" in kwargs:
            headers = {**headers, "Content-Type": "application/json"}
            logger.debug("found json in kwargs")

        logger.debug("headers before req build: " + str(headers))
        logger.debug("query before req build: " + str(query))

        req = requests.Request(method, url, headers=headers, data=query, **kwargs)
        logger.debug("managed to build request")
        try:
            resp = self.session.send(req.prepare())
        except Exception as e:
            logger.error(f"Failed to send request. Error: {e}")
            raise

        if resp.status_code == 401:
            logger.warning("Received status 401. Requesting new access token.")
            self.get_token()
            resp = self.session.send(req.prepare())
        return resp
