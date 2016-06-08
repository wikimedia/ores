"""
This module provides a :class:`ores.api.Session` class that can maintain a
connection to an instance of ORES and efficiently generate scores.

.. autoclass:: ores.api.Session
    :members:
"""
import logging
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

import requests
import requests.adapters
from more_itertools import chunked

logger = logging.getLogger(__name__)


class Session:
    """
    Constructs a session with an ORES API and provides facilities for scoring
    revisions in batch and parallel.

    :Parameters:
        host : str
            The host of ORES to connect to (preceed with http:// or https://)
        user_agent : str
            A User-Agent header to send with every request
        batch_size : int
            The number of scores to batch per request.
        parallel_request : int
            The maximum number of requests to make in parallel
        retries : int
            The maximum number of retries for basic HTTP errors before giving
            up
    """
    DEFAULT_USERAGENT = "ORESapi default user-agent"

    def __init__(self, host, user_agent=None, batch_size=50,
                 parallel_requests=4, retries=5):
        self.host = str(host)
        self.batch_size = int(batch_size)
        self.workers = int(parallel_requests)
        self.retries = int(retries)

        self._session = requests.Session()
        self._session.mount(self.host,
                            requests.adapters.HTTPAdapter(max_retries=retries))
        self.headers = {}
        if user_agent is None:
            logger.warning("Sending requests with default User-Agent.  " +
                           "Set 'user_agent' on oresapi.Session to " +
                           "quiet this message.")
            self.headers['User-Agent'] = self.DEFAULT_USERAGENT
        else:
            self.headers['User-Agent'] = user_agent

    def score(self, context, model, revids):
        """
        Genetate scores for model applied to a sequence of revisions.

        :Parameters:
            context : str
                The name of the context -- usually the database name of a wiki
            model : str
                The name of a model to apply
            revids : `iterable`
                A sequence of revision IDs to score.
        """
        if isinstance(revids, int):
            rev_ids = [revids]
        else:
            rev_ids = [int(rid) for rid in revids]

        return self._score(context, model, rev_ids)

    def _score(self, context, model, rev_ids):
        logging.debug("Starting up thread pool with {0} workers"
                      .format(self.workers))
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = []
            for rev_id_batch in chunked(rev_ids, self.batch_size):
                rev_id_batch = list(rev_id_batch)
                logging.debug("Starting batch of {0} revids"
                              .format(len(rev_id_batch)))
                futures.append(executor.submit(self._score_request,
                                               context, model,
                                               rev_id_batch))

            for future in futures:
                for score in future.result():
                    yield score

    def _score_request(self, context, model, rev_ids):
        url = self.host + "/v2/scores/{0}/{1}/" \
                          .format(urllib.parse.quote(context),
                                  urllib.parse.quote(model))

        params = {'revids': "|".join(str(rid) for rid in rev_ids)}
        logging.debug("Sending score request for {0} revisions"
                      .format(len(rev_ids)))
        start = time.time()
        response = requests.get(url, params=params,
                                headers=self.headers,
                                verify=True, stream=True)
        try:
            doc = response.json()
        except ValueError:
            raise RuntimeError("Non-json response: " + response.text[:100])

        logging.debug("Score request completed for " +
                      "{0} revisions completed in {1} seconds"
                      .format(len(rev_ids), round(time.time() - start, 3)))

        if 'error' in doc:
            # TODO: custom class
            raise RuntimeError(doc['error'])

        if 'warnings' in doc:
            for warning_doc in doc['warnings']:
                logger.warn(warning_doc)

        return [doc['scores'][context][model]['scores'][str(rev_id)]
                for rev_id in rev_ids]
