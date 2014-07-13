#!/usr/bin/env python

import argparse
import re
from multiprocessing.pool import ThreadPool as Pool
import requests
import bs4
from pytube import YouTube
from urlparse import urlparse


# root_url = 'http://pyvideo.org'
# index_url = root_url + '/category/50/pycon-us-2014'

# root_url = 'http://pyvideo.org'
# index_url = root_url + '/category/51/scipy-2014'


def download_yt_video(yt_url, filename, path):
    yt = YouTube()
    yt.url = yt_url
    print path
    yt.filename = filename
    max_res = yt.filter('mp4')[-1].resolution
    video = yt.get('mp4', max_res)
    video.download(path, verbose=False)


def get_video_page_urls(index_url):
    response = requests.get(index_url)
    soup = bs4.BeautifulSoup(response.text)
    return soup.title.string, [a.attrs.get('href') for a in
            soup.select('div.video-summary-data a[href^=/video]')]


def get_video_data(video_page_url):
    video_data = {}
    response = requests.get(video_page_url)
    soup = bs4.BeautifulSoup(response.text)
    video_data['title'] = soup.select('div#videobox h3')[0].get_text()
    video_data['speakers'] = [a.get_text() for a in
                              soup.select('div#sidebar a[href^=/speaker]')]
    try:
        video_data['youtube_url'] = soup.select('div#sidebar a[href^=http://www.youtube.com]')[0].get_text()
        response = requests.get(video_data['youtube_url'], headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36'})
        soup = bs4.BeautifulSoup(response.text)
        video_data['views'] = int(re.sub('[^0-9]', '',
                                         soup.select('.watch-view-count')[0].get_text().split()[0]))
        video_data['likes'] = int(re.sub('[^0-9]', '',
                                         soup.select('.likes-count')[0].get_text().split()[0]))
        video_data['dislikes'] = int(re.sub('[^0-9]', '',
                                            soup.select('.dislikes-count')[0].get_text().split()[0]))
    except:
        # video does not have a youtube URL
        video_data['views'] = 0
        video_data['likes'] = 0
        video_data['dislikes'] = 0
    return video_data


def parse_args():
    parser = argparse.ArgumentParser(description='Show PyCon 2014 video statistics.')
    # parser.add_argument('--site', default='http://pyvideo.org/category/50/pycon-us-2014')
    parser.add_argument('pyvidsite', help='specify the pyvideo site you want to scrape')
    parser.add_argument('--sort', metavar='FIELD', choices=['views', 'likes', 'dislikes'], default='views',
                        help='sort by the specified field. Options are views, likes and dislikes.')
    parser.add_argument('--max', metavar='MAX', type=int, help='show the top MAX entries only.')
    parser.add_argument('--csv', action='store_true', default=False,
                        help='output the data in CSV format.')
    parser.add_argument('--workers', type=int, default=8,
                        help='number of workers to use, 8 by default.')
    parser.add_argument('--download', action='store_true', default=False,
                        help='download each video from youtube.com')
    parser.add_argument('--path', default='./',
                        help='path where to save the videos')
    return parser.parse_args()


def show_video_stats(options):
    index_url = options.pyvidsite
    root_url = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse( index_url ))
    pool = Pool(options.workers)
    video_page_title, video_page_urls = get_video_page_urls(index_url)
    for i in range(len(video_page_urls)):
        video_page_urls[i] = root_url + video_page_urls[i][1:]
    results = sorted(pool.map(get_video_data, video_page_urls), key=lambda video: video[options.sort],
                     reverse=True)
    print('\nPage name: {}'.format(video_page_title))
    print('Total Number of Talks: {}'.format(len(results)))
    max = options.max
    if max is None or max > len(results):
        max = len(results)
    if options.csv:
        print(u'"title","speakers", "views","likes","dislikes"')
    else:
        print(u'Views  +1  -1 Title (Speakers)')
    for i in range(max):
        if options.csv:
            print(u'"{0}","{1}",{2},{3},{4}'.format(
                results[i]['title'], ', '.join(results[i]['speakers']), results[i]['views'],
                results[i]['likes'], results[i]['dislikes']))
        else:
            if options.download:
                dl_tag = '-- Downloading...'
            else:
                dl_tag = ''
            print(u'{0:5d} {1:3d} {2:3d} {3} ({4}) {5}'.format(
                results[i]['views'], results[i]['likes'], results[i]['dislikes'], results[i]['title'],
                ', '.join(results[i]['speakers']), dl_tag))
        if options.download:
            download_yt_video(results[i]['youtube_url'], ' - '.join([results[i]['title'], ', '.join(results[i]['speakers'])]), options.path)


if __name__ == '__main__':
    show_video_stats(parse_args())
