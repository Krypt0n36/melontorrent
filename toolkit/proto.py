import requests
import urllib.parse


def reqPeerList(tracker_url, params):
    h = urllib.parse.quote_plus(params['info_hash'])
    params_url = '?info_hash=%s&peer_id=%s&port=1000&uploaded=0&downloaded=0&ip=123.122.123.1&left=100'%(h, params['peer_id'])
    print(tracker_url + params_url)
    r = requests.get(tracker_url + params_url)
    print(r.status_code)

reqPeerList('http://bt1.archive.org:6969/announce', {
    'info_hash': 'f1573ececa8042688dc423e6474e1a9db27222ef',
    'peer_id': 'cdoba3136at9i3hzauwj'
})
