# -*- coding: utf-8 -*-
# Copyright (c) 2012 Sebastian Wehrmann
# See also LICENSE.txt

import httplib2

API_URL_V1 = ('http://nikeplus.nike.com/nikeplus/v1/services/widget/'
              'get_public_run_list.jsp?userID=')


class NikePlusFetcher(object):
    """Retrieve workout data from the NikePlus service page.

    Caches the last successful response for times, where the service is out of
    order.

    Arguments:

        user_id:    Your user id (usually an integer)

    """

    last_valid_content = None

    def __init__(self, user_id):
        self.user_id = user_id
        self.http = httplib2.Http(".cache")

    def fetch(self, force=False):
        """Fetch data from the server.

        The argumennt `force` can be used to force the retrieval of data
        regardless to HTTP caching and Nike+ service status.

        """

        headers = {}
        if force:
            headers['Cache-Control'] = 'co-cache'

        url = API_URL_V1 + str(self.user_id)
        resp, content = self.http.request(url, headers=headers)

        status = int(resp['status'])
        if status == 200:
            self.last_valid_content = content
        response = self.last_valid_content if not force else content
        return status, response
