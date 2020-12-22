import os
import time
import requests
from threading import Thread


class VkGroupParser:
    def __init__(self):
        # getting data from files
        with open('./in/vk_group_ids.txt', 'r', encoding='utf-8') as file:
            self.group_ids = [x for x in file.read().split('\n') if x]
        with open('./in/vk_token.txt', 'r', encoding='utf-8') as file:
            self.token = file.read().split('\n')[0]

        self.threads_count = 2

    def parse(self, owner_id):
        # parse vk.com wall
        self.links = []
        print(f'parsing group {owner_id}')
        wall = requests.get('https://api.vk.com/method/wall.get', params={'access_token': self.token,
                                                                          'v': '5.103',
                                                                          'owner_id': owner_id,
                                                                          }).json()
        ct = wall['response']['count'] // 100 + 1
        print(wall['response']['count'])
        offset = 0
        count = 100
        for x in range(ct):
            wall = requests.get('https://api.vk.com/method/wall.get', params={'access_token': self.token,
                                                                              'v': '5.103',
                                                                              'owner_id': owner_id,
                                                                              'count': count,
                                                                              'offset': offset
                                                                              }).json()

            for x in wall['response']['items']:
                try:
                    for y in x['attachments']:
                        self.links.append([y['photo']['sizes'][-1]['url'], y['photo']['id']])
                except:
                    pass
            offset += 100

    def download(self):
        # download images
        try:
            os.mkdir('out')
        except:
            pass
        for thread_num in range(self.threads_count):
            Thread(target=self.downloading_thread, args=(self.links[thread_num::self.threads_count],)).start()
            time.sleep(0.1)

    def downloading_thread(self, links_package):
        for x in links_package:
            print(f'downloading {self.links.index(x)} in {len(self.links)}')
            photo = requests.get(x[0])
            with open('out\\' + str(x[1]) + '.jpg', 'wb') as f:
                f.write(photo.content)

    def run(self):
        for group_id in self.group_ids:
            self.parse(group_id)
            print(f'downloading {group_id}')
            self.download()


if __name__ == '__main__':
    bot = VkGroupParser()
    bot.run()
