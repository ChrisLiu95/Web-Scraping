# coding:utf-8
# __author__: ChrisLiu
"""
grab information of a film website
data cleaning
output the most relevant comment of some movies

"""

from urllib import request
from bs4 import BeautifulSoup as bs
import re
import jieba
import pandas as pd
import numpy
import matplotlib.pyplot as plt
import matplotlib
from wordcloud import WordCloud


def getNowplayingMovie_list():
    resp = request.urlopen("https://movie.douban.com/cinema/nowplaying/hangzhou/")
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data, "html.parser")
    nowplaying_movie = soup.findAll('div', id='nowplaying')
    # print(nowplaying_movie[0])
    nowplaying_movie_list = nowplaying_movie[0].findAll('li', class_='list-item')
    # print(nowplaying_movie_list[1])
    movielist = []
    for item in nowplaying_movie_list:
        movie_dic = {}
        movie_dic['id'] = item['data-subject']
        movie_dic['name'] = item['data-title']
        movielist.append(movie_dic)
    return movielist


# comment section
def getCommentsByID(movieId, pageNum):
    commentlist = []
    if pageNum > 0:
        start = (pageNum - 1) * 20
    else:
        return False
    comment_url = 'http://movie.douban.com/subject/' + movieId + '/comments' + '?' + 'start' + str(start) + '&limit=20'
    resp = request.urlopen(comment_url)
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data, "html.parser")
    comment = soup.findAll('div', class_='comment')
    for item in comment:
        if item.findAll('p')[0].string is not None:
            commentlist.append(item.findAll('p')[0].string)
    return commentlist


def main():
    commentlist = []
    movielist = getNowplayingMovie_list()
    f = open('movie.txt', 'a')
    for item in movielist:
        string = str(item)
        f.write(string)
        f.write('\r\n')
    f.close()
    for num in range(1, 5):
        commentlist_temp = getCommentsByID(movielist[4]['id'], num)
        commentlist.append(commentlist_temp)

    comments = ''
    for item in commentlist:
        comments = comments + str(item).strip()
    # print(comments)

    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    filter_data = re.findall(pattern, comments)
    cleaned_comments = ''.join(filter_data)

    segment = jieba.lcut(cleaned_comments)
    word_df = pd.DataFrame({'segment': segment})

    # quoting=3 全部引用
    stopwords = pd.read_csv("/Users/Lxc/Desktop/stopwords.txt", index_col=False, quoting=3,
                            names=['stopword'], encoding='utf-8')
    word_df = word_df[~word_df.segment.isin(stopwords.stopword)]
    print(word_df.head())

    # 词频统计
    word_stat = word_df.groupby(by=['segment'])['segment'].agg({'count': numpy.size})
    word_stat = word_stat.reset_index().sort_values(by=['count'], ascending=False)
    print(word_stat.head())

    # # 画图显示高频词
    matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)
    wordcloud = WordCloud(font_path='simhei.ttf', background_color='white', max_font_size=80)
    word_frequence = {x[0]: x[1] for x in word_stat.head(1000).values}
    word_frequence_list = []
    for key in word_frequence:
        temp = (key, word_frequence[key])
        word_frequence_list.append(temp)

    f = open('word_frequence.txt', 'a')
    for item in word_frequence_list:
        string = str(item)
        f.write(string)
        f.write('\r\n')
    f.close()

    wordcloud = wordcloud.fit_words(word_frequence)
    plt.imshow(wordcloud)
    plt.savefig("result.png")
    plt.show()


main()
