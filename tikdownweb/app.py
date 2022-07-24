import io
import os
import re
import sys
import time

import requests

from flask import Flask
from flask import request
from flask import render_template
from flask import make_response, send_file, Response, stream_with_context

app = Flask(__name__)

cache = []


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/pic')
def getpic():
    return send_file(os.path.join(BASE_DIR, 'a.png'), as_attachment=True)
    # return send_file(os.path.join(BASE_DIR, 'videos', '20220724PM091803.mp4'), as_attachment=True)


@app.route('/download', methods=['POST', 'GET'])
def download():
    url = request.json.get('msg')
    print(url)
    inner_url = parse_url(url)
    download_video_web(inner_url)
    return Response({'code': 200})


@app.route('/getvideo')
def getlastOne():
    name = cache[-1]
    return send_file(os.path.join(BASE_DIR, 'videos', name), as_attachment=True, download_name=f"{name}.mp4")


def parse_url(full_share_url):
    """提取分享链接中 真正的视频url"""
    full_share_url.replace('\n', '')
    if not full_share_url:
        return
    # 正则匹配search得到对象
    inner_url = re.search(r'(http.+[^ ])', full_share_url).group(0)
    return inner_url


def download_video_web(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                      'like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 '
    }
    print('最初的地址', url)
    r1 = requests.get(url=url, headers=headers, allow_redirects=False)
    url2 = r1.headers.get('location')
    print('访问最初url后 要求302到', url2)

    # 获取url2后面的关键id
    vid = re.search(r'/video/(\d+)/', url2).group(1)
    base_url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='
    r_json = requests.get(url=base_url + vid, headers=headers).json()

    title = time.strftime('%Y%m%d%p%I%M%S')
    url3 = r_json.get('item_list')[0].get('video').get('play_addr').get('url_list')[0]
    final_url = url3.replace('playwm', 'play')
    video_response = requests.get(url=final_url, headers=headers, stream=True)

    path = os.path.join(BASE_DIR, 'videos', f'{title}.mp4')
    with open(path, 'wb') as fp:
        fp.write(video_response.content)

    cache.append(title + '.mp4')


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    print(BASE_DIR)
    if not os.path.exists(os.path.join(BASE_DIR, 'videos')):
        os.mkdir(os.path.join(BASE_DIR, 'videos'))
    app.run(host='0.0.0.0', port=5001, debug=True)
