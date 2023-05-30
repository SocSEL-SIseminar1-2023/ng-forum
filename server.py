"""サーバを起動し、クライアント要求に応じてレスポンスを返す"""
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server, WSGIServer
import copy
import hashlib
import json
import subprocess
import time
import judge



messages = []
"""
[
    {
        'player_id': 送信プレイヤの固有文字列,
        'body': メッセージ本文,
        'ng': 送信プレイヤのNG行動,
        'judge': 'アウト' or 'セーフ',
    }
    ...
]
"""



players = {}
"""
{
    クライアントから送信されるトークン文字列: {
        'player_id': プレイヤの固有文字列,
        'ng[]': プレイヤのNG行動,
        'checker': NG行動を判定する関数（引数は判定したいメッセージ）,
        'sequence': 最後に返答したときのメッセージ数
        
    }
    ...
]
"""



class App:
    """URLに応じてレスポンスを返す
    """


    def __init__(self, start_response):
        self.start_response = start_response



    def read_messages(self, token):
        """クライアントにメッセージ一覧を返す

        新しいメッセージがあるまで待機してからクライアントにメッセージ一覧を返す

        :param self: このクラス
        :type self: App
        :param token: クライアントを判別するトークン
        :type token: str
        :return: バイナリ文字列化したメッセージの一覧
        :rtype: list
        """
        if token in players:
            # 最大1時間待つ
            for _ in range(3600):
                # 前回の返答からメッセージが増えるまで返答を待機する
                if players[token]['sequence'] < len(messages):
                    break
                time.sleep(1)
            players[token]['sequence'] = len(messages)
        else:
            # 新しいプレイヤの追加
            ng_rule, checker = judge.get_random_ng()
            players[token] = {
                'player_id': hashlib.md5(token.encode('utf-8')).hexdigest(),
                'ng': [ng_rule],
                'checker': checker,
                'sequence': len(messages),
                'count': 0,
            }
        # 受信プレイヤのNG行動を隠して返答する
        result_messages = copy.deepcopy(messages)
        for message in result_messages:
            if message['player_id'] == players[token]['player_id']:
                message['ng'] = '?'
        self.start_response('200 OK', [('Content-type', 'application/json')])
        return [json.dumps(result_messages).encode('utf-8')]


    def insert_message(self, message):
        """新しいメッセージをメッセージ一覧に追加する

        新しいメッセージメッセージ一覧に追加し、クライアントに完了レスポンスを返す

        :param self: このクラス
        :type self: App
        :param message: 追加するメッセージ
        :type message: dict
        :return: 空のバイナリ文字列
        :rtype: list
        """
        messages.append({
            'player_id': players[message['token']]['player_id'],
            'body': message['body'],
            'ng': players[message['token']]['ng'],
            'judge': "アウト" if players[message['token']]['checker'](message['body']) else 'セーフ',
        })
        players[message['token']]['count'] += 1
        self.start_response('200 OK', [('Content-type', 'application/json')])
        return b''



    def index_html(self):
        """クライアントにindex.htmlの文章を返す

        page/index.htmlを読み込み、文章をクライアントに返す

        :param self: このクラス
        :type self: App
        :return: バイナリ文字列化したindex.htmlの文章
        :rtype: list
        """
        self.start_response('200 OK', [('Content-type', 'text/html')])
        with open('page/index.html', encoding='utf-8') as file:
            return [file.read().encode('utf-8')]



    def main_js(self):
        """クライアントにmain.jsの文章を返す

        page/main.jsを読み込み、文章をクライアントに返す

        :param self: このクラス
        :type self: App
        :return: バイナリ文字列化したmain.jsの文章
        :rtype: list
        """
        self.start_response('200 OK', [('Content-type', 'text/javascript')])
        with open('page/main.js', encoding='utf-8') as file:
            return [file.read().encode('utf-8')]



    def style_css(self):
        """クライアントにstyle.cssの文章を返す

        page/style.cssを読み込み、文章をクライアントに返す

        :param self: このクラス
        :type self: App
        :return: バイナリ文字列化したstyle.cssの文章
        :rtype: list
        """
        self.start_response('200 OK', [('Content-type', 'text/css')])
        with open('page/style.css', encoding='utf-8') as file:
            return [file.read().encode('utf-8')]



    def not_found(self):
        """クライアントにNot Foundレスポンスを返す

        クライアントにNot Foundレスポンスを返す

        :param self: このクラス
        :type self: App
        :return: 空のバイナリ文字列
        :rtype: list
        """
        self.start_response('404 Not Found', [])
        return b''



def app(environ, start_response):
    """クライアントの要求に応じてレスポンスを返す

    クライアントの要求に応じてファイルやJSONデータを返す

    :param environ: クライアントからの要求情報
    :type environ: dict
    :param start_response: レスポンスのステータスコードとヘッダーを設定するためのメソッド
    :type start_response: method
    :return: クライアントの要求に応じたバイナリ文字列
    :rtype: list
    """
    response = App(start_response)
    query = parse_qs(environ['QUERY_STRING'])
    # URLに応じて返答する
    if environ['PATH_INFO'] == '/':
        return response.index_html()
    if environ['PATH_INFO'] == '/main.js':
        return response.main_js()
    if environ['PATH_INFO'] == '/style.css':
        return response.style_css()
    if environ['PATH_INFO'] == '/messages':
        return response.read_messages(query['token'][0])
    if environ['PATH_INFO'] == '/post':
        return response.insert_message(
            json.loads(environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0))))
        )
    return response.not_found()



# サーバを起動する
with make_server('', 8080, app, type('', (ThreadingMixIn, WSGIServer), {})) as httpd:
    subprocess.run('echo Serving on https://8080-$WEB_HOST', shell=True, check=False)
    httpd.serve_forever()
