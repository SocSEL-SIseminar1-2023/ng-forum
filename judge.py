"""NG行動名とNG判定関数を提供する"""
import random
import re

def is_more_than_30_chars(message):
    """メッセージが30文字以上か判定する

    len()を用いてメッセージが30文字以上か判定し、bool値を返す

    :param message: 判定するメッセージ
    :type message: str
    :return: メッセージが30文字以上ならばTrue、それ以外でFalse
    :rtype: bool
    """
    return len(message) >= 30



# bug: 大きな素数を入れると処理に時間がかかる（例 2147483647）
def contains_prime_number(message):
    """メッセージが素数を含むか判定する

    メッセージに1つ以上の素数が含まれるか判定し、bool値を返す

    :param message: 判定するメッセージ
    :type message: str
    :return: メッセージに1つ以上の素数があればTrue、それ以外でFalse
    :rtype: bool
    """
    # 文章中の整数numberを順番に取り出す
    for number in map(int, re.findall(r'\d+', message)):
        # nが2未満ならスキップ
        if number < 2:
            continue
        # nが2≦i<nで割り切れるかチェック
        is_prime = True
        for i in range(2, number):
            if number % i == 0:
                is_prime = False
                break
        if is_prime:
            return True

    return False



def contains_junishi_animal(message):
    """メッセージが十二支の動物を含むか判定する

    メッセージに1つ以上の十二支の動物が含まれるか判定し、bool値を返す

    :param message: 判定するメッセージ
    :type message: str
    :return: メッセージに1つ以上の十二支の動物があればTrue、それ以外でFalse
    :rtype: bool
    """

    return message in ('子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥',
    'ネズミ','ウシ','トラ','ウサギ','リュウ','ヘビ','ウマ','ヒツジ','サル','トリ','イヌ','イノシシ',
    'ねずみ','うし','とら','うさぎ','りゅう','へび','うま','ひつじ','さる','とり','いぬ','いのしし')

def contains_kanji_even(message):
    """メッセージに同一の漢字が偶数回出現しているかを判定する

    メッセージの漢字の個数を数え、bool値を返す

    正規表現で漢字かどうかを判定（kanjiに格納される）
    :return: メッセージ内に同一の漢字偶数個あればTrue、それ以外でFalse
    :rtype: bool
    """
    for kanji in set(re.findall(r'[\u4E00-\u9FD0]', message)):
        if message.count(kanji) % 2 == 0:
            return True
    return False

    
    
    

def get_random_ng():
    """ランダムなNG行動名とNG判定関数を返す

    ランダムなNG行動名と、メッセージがNG行動に該当するか判定する関数を返す

    :return: ランダムなNG行動名とNG判定関数
    :rtype: (str, function)
    """
    return random.choice([
        ('30文字以上の文章', is_more_than_30_chars),
        ('素数を含む文章', contains_prime_number),
        ('十二支の動物を含む文章', contains_junishi_animal),
        ('同じ漢字を偶数回出現する文章',contains_kanji_even),
    ])
