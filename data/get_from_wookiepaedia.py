import argparse
import re

from bs4 import BeautifulSoup
from requests_html import HTMLSession, TimeoutError

import pandas as pd


class TimelineCannonMedia:

    def __init__(self):

        self.args = self.arg_parser()
        self.url = 'https://starwars.fandom.com/wiki/Timeline_of_canon_media'

    def arg_parser(self):

        args_dict = {}

        parser = argparse.ArgumentParser(description = 'Get ordered media (movies and TV) - watch order by cannon chronological order')

        parser.add_argument('-f', '--film', help = 'Get movies marked as films', action = 'store_true')
        parser.add_argument('-t', '--tv', help = 'Get movies marked as TV', action = 'store_true')
        parser.add_argument('-a', '--remove_children', help = 'Remove entrys relating to childrens content', action = 'store_true')

        args = parser.parse_args()

        for media_type in vars(args):
            args_dict[media_type] = getattr(args, media_type)

        return args_dict

    def read_in_page(self):

        session = HTMLSession()

        r = session.get(self.url)

        if not r.ok:
            raise TimeoutError(f'Unable to connect to site {r.status_code}')

        return r

    def read_in_page_local(self):

        with open('test.html', 'r') as input_handle:

            output = '\n'.join(input_handle.readlines())

        return output

    def matches_childrens_media(self, show_name):

        contains_childrens_media = False

        childrens_media = ['Star Wars: Young Jedi Adventures',
                           'Star Wars: Fun with Nubs',
                           'Star Wars: Jedi Temple Challenge',
                           'Star Wars Forces of Destiny',
                           'Star Wars Galaxy of Adventures',
                           '"Hunted"',
                           'Grogu Cutest In The Galaxy']

        for childrens_show_name in childrens_media:
            if re.match(f'^{childrens_show_name}', show_name):
                contains_childrens_media = True

        return contains_childrens_media

    def clean_title(self, title_to_clean):

        cleaned_title = title_to_clean

        cleaned_title = re.sub(r'†(\s)?$', '', cleaned_title)

        cleaned_title = cleaned_title.strip()

        return cleaned_title

    def read_in_data(self):

        # From Wookiepaedia
        # html_response_url = self.read_in_page()
        # html_response = BeautifulSoup(html_response_url.html.html, 'html.parser')

        # From local HTML file
        html_response_url = self.read_in_page_local()
        html_response = BeautifulSoup(html_response_url, 'html.parser')

        media_types_list = {}

        citation_pattern = re.compile(r'\[\d{1,}\]$')

        dict_keys = []

        watch_order_id = 0

        for media_type in self.args:
            if self.args[media_type] is True:
                dict_keys.append(media_type)

        table = html_response.find('table', {'id': 'prettytable', 'class': 'wikitable'})

        table_rows = table.find_all('tr')

        for row in table_rows:

            if not 'class' in row.attrs:
                continue

            row_class = row.attrs['class']

            if 'unpublished' in row_class:
                continue

            if row_class[0] not in dict_keys:
                continue

            watch_order_id += 1

            row_tds = row.find_all('td')
            row_date = re.sub(citation_pattern, '', row_tds[0].text)

            media_type_wookiepeadia = row_tds[1].text.strip()

            show_title = row_tds[2].text.strip()

            show_title_list = show_title.split('\n', 1)

            if len(show_title_list) == 1:
                show_title = show_title_list[0]
                note = ''
            else:
                show_title, note = show_title_list

            show_and_episode = self.clean_title(show_title)

            if re.match('^.*? — ".*?"$', show_and_episode):
                show, episode_title = show_and_episode.split(' — ')

            else:
                show = show_and_episode
                episode_title = ''

            show = re.sub(r'\s{2,}', ' ', show)
            episode_title = re.sub(r'\s{2,}', ' ', episode_title)

            if self.matches_childrens_media(show) is True:
                continue

            release_date = row_tds[3].text.strip()

            media_types_list[watch_order_id] = {'cannon_date': row_date,
                                                'media_type': row_class[0],
                                                'show': show,
                                                'title': episode_title,
                                                'media_release_date': release_date,
                                                'note': note}

        media_pd = pd.DataFrame.from_dict(media_types_list, orient = 'index')
        media_pd[['media_release_date']] = media_pd[['media_release_date']].apply(pd.to_datetime)

        show_unique_values = media_pd['show'].unique()

        print(media_pd)

