import json
import logging
import urllib
import urlparse

import httplib2

class EZCometError(RuntimeError):
    """EZComet API error
    
    """

class EZCometAPI(object):
    
    ENDPOINT = 'api.ezcomet.com'
    
    def __init__(
        self, 
        api_key, 
        user_name, 
        ssl=True, 
        endpoint=None, 
        logger=None
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.api_key = api_key
        self.user_name = user_name
        self.ssl = ssl
        self._endpoint = endpoint or self.ENDPOINT 
        
    @property
    def base_url(self):
        if self.ssl:
            return 'https://' + self._endpoint
        return 'http://' + self._endpoint
    
    @property
    def cacerts_path(self):
        import os
        import ezcomet
        pkg_dir = os.path.dirname(ezcomet.__file__)
        return os.path.join(pkg_dir, 'cacerts.txt')
    
    def _post(self, args):
        query = urllib.urlencode(args)
        headers = {
            'Content-type': 'application/x-www-form-urlencoded; charset=utf-8'
        }
        url = urlparse.urljoin(self.base_url, 'write')
        
        conn = httplib2.Http(ca_certs=self.cacerts_path)
        resp, content = conn.request(
            url, 
            method='POST', 
            body=query, 
            headers=headers
        )
        json_data = json.loads(content)
        if resp.status != 200:
            msg = json_data['msg']
            raise EZCometError('Failed to call write API (%s)' % msg)
        return json_data
        
    def write(self, channel, msg, tick=None):
        """Write a message to EZComet.com and return tick
        
        """
        self.logger.info('Write to channel %r with msg %r', channel, msg)
        qname = '%s-%s' % (self.user_name, channel)
        args = dict(
            qname=qname,
            msg=msg.encode('utf8'),
            api_key=self.api_key
        )
        if tick is not None:
            args['tick'] = tick
        json_data = self._post(args)
        return json_data['tick']
    
    def flush(self, channel):
        """Flush messages in a channel
        
        """
        self.logger.info('Flush channel %s', channel)
        qname = '%s-%s' % (self.user_name, channel)
        args = dict(
            qname=qname,
            api_key=self.api_key,
            flush=1
        )
        json_data = self._post(args)
        return json_data['code']
    
def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Write a message to EZComet.com')
    parser.add_argument('-k', '--api-key', dest='api_key', 
                        action='store',
                        help='API key of your EZComet service')
    parser.add_argument('-u', '--user-name', dest='user_name', 
                        action='store',
                        help='Username of your EZComet service')
    parser.add_argument('-s', '--no-ssl', action='store_const', 
                        dest='ssl', default=True, const=False,
                        help='Do not use SSL')
    parser.add_argument('-f', '--flush', action='store_const', 
                        dest='flush', default=False, const=True,
                        help='Flush messages in the channel')
    parser.add_argument('channel', metavar='CHANNEL', type=str,
                        help='name of channel to write')
    parser.add_argument('msg', metavar='MESSAGE', nargs='?', type=str,
                        help='message to write')
    args = parser.parse_args()
    
    api = EZCometAPI(
        api_key=args.api_key,
        user_name=args.user_name,
        ssl=args.ssl,
    )
    if args.flush:
        code = api.flush(args.channel)
        print code
    else:
        tick = api.write(args.channel, args.msg)
        print tick
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()