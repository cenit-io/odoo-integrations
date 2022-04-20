import requests
import xmltodict


class PrestashopError(RuntimeError):
    pass


class PrestashopApi:
    STATUSES = (200, 201)

    def __init__(self, api, key):
        self.api = api
        self.key = key

    def _get_url(self, path):
        return self.api + '/' + path

    def _check_response(self, res, ret):
        if res.status_code not in self.STATUSES:
            raise PrestashopError('Status %s, %s' % (res.status_code, ret))
        return ret

    def _request(self, method, path, params=None, data=None, files=None):
        if data is not None:
            data = xmltodict.unparse({'prestashop': data}).encode('utf-8')
        res = requests.request(method, self._get_url(path), auth=(self.key, ''), params=params, data=data, files=files)
        return self._check_response(res, xmltodict.parse(res.text)['prestashop'] if not files and res.text else None)

    def add(self, path, data):
        return self._request('POST', path, data=data)

    def add_image(self, path, fp, exists=False):
        with open(fp, 'rb') as fp:
            return self._request('POST', 'images/' + path, {'ps_method': 'PUT'} if exists else None,
                                 files={'image': fp})

    def get(self, path, params=None):
        return self._request('GET', path, params)

    def edit(self, path, data):
        return self._request('PUT', path, data=data)

    def delete(self, path):
        return self._request('DELETE', path)
