from flask import Flask, request, jsonify, send_from_directory
import requests, base64, time, os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

def upload_to_imgbb(image_url, keyword):
    try:
        print(f"准备上传图片：{image_url}")
        img_data = requests.get(image_url).content
        encoded = base64.b64encode(img_data).decode('utf-8')
        upload_url = 'https://api.imgbb.com/1/upload'
        response = requests.post(upload_url, data={
            'key': IMGBB_API_KEY,
            'image': encoded,
            'name': f"{keyword}_{int(time.time())}"
        })
        result = response.json()
        return result['data']['url']
    except Exception as e:
        print(f"上传失败: {e}")
        return None

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

@app.route('/search')
def search():
    query = request.args.get('q')
    platform = request.args.get('platform')
    print(f"收到请求：关键词={query}, 平台={platform}")
    if not query or not platform:
        return jsonify({'error': '缺少关键词或平台'}), 400

    image_urls = []
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        if platform == 'bing':
            search_url = f"https://www.bing.com/images/search?q={query}"
            r = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            imgs = soup.find_all('img')
            print(f"Bing 抓到图片数：{len(imgs)}")
            for img in imgs:
                src = img.get('src')
                if src and 'http' in src:
                    uploaded = upload_to_imgbb(src, query)
                    if uploaded:
                        image_urls.append(uploaded)

        elif platform == 'pinterest':
            search_url = f"https://www.pinterest.com/search/pins/?q={query}"
            r = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            imgs = soup.find_all('img')
            print(f"Pinterest 抓到图片数：{len(imgs)}")
            for img in imgs:
                src = img.get('src')
                if src and 'http' in src:
                    uploaded = upload_to_imgbb(src, query)
                    if uploaded:
                        image_urls.append(uploaded)

        elif platform == 'xhs':
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={query}"
            r = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            imgs = soup.find_all('img')
            print(f"小红书 抓到图片数：{len(imgs)}")
            for img in imgs:
                src = img.get('src')
                if src and 'http' in src and 'xhslink.com' not in src:
                    uploaded = upload_to_imgbb(src, query)
                    if uploaded:
                        image_urls.append(uploaded)

        elif platform == 'weibo':
            search_url = f"https://s.weibo.com/weibo?q={query}"
            r = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            imgs = soup.find_all('img')
            print(f"微博 抓到图片数：{len(imgs)}")
            for img in imgs:
                src = img.get('src')
                if src and 'http' in src:
                    uploaded = upload_to_imgbb(src, query)
                    if uploaded:
                        image_urls.append(uploaded)

        else:
            return jsonify({'error': '不支持的平台'}), 400

        return jsonify({'images': image_urls[:15]})

    except Exception as e:
        print(f"整体处理失败: {e}")
        return jsonify({'error': f'抓图失败: {e}'}), 500
