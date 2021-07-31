from os import path
import pathlib
import json
import asyncio

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

scriptDirectory = pathlib.Path().absolute()

class Television(webdriver.Chrome):

    def __init__(self, *args, **kwargs):
        # Set chromium flags
        options = Options()
        options.add_argument('-kiosk')
        options.add_argument(f"user-data-dir={path.join(scriptDirectory, 'userdata')}")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches",["enable-automation"])
        if 'options' in kwargs:
            del kwargs['options']
        super().__init__(*args, options=options, **kwargs)

        # Television variables
        with open('shows.json', encoding='utf-8') as f:
            self.allowed_shows = json.load(f)
        with open('settings.json', encoding='utf-8') as f:
            self.settings = json.load(f)
        self.state = None
        self.links = dict()

    async def get_show(self, name: str):
        self.state = 'menu'
        self.get(self.allowed_shows[name]['link'])

        self.find_element_by_xpath('//div[@class="select select--drop-down select--default select select--sort"]//button[@aria-controls="episodeSortingContainer"]').click()
        self.find_element_by_xpath('//div[@aria-expanded="true"]//li[@class="select__item"]').click()

        await asyncio.sleep(1) # TODO - Make it wait dynamically
        episodes = dict()
        for item in self.find_elements_by_class_name('d2-item'):
            episode = item.find_element_by_class_name('d2-item__title').get_attribute('innerHTML')
            premium = bool(item.find_elements_by_class_name('premium-icon'))
            if not premium:
                episodes[episode] = premium
            self.links[int(episode[3:])] = item.find_element_by_class_name('d2-item__title').get_attribute('href')
        return {'episodes': episodes, 'success': True}
        
    async def watch(self, show: str):
        if show not in self.links:
            return False
        self.get(self.links[show])
        self.state = 'video'
        while self.execute_script('return KalturaHB.videoObj?.getLastState() !== "PLAYING";'):
            await asyncio.sleep(0)

        # Set volume. Not sure why need to send the keys, but it doesn't work if I don't
        self.find_element_by_tag_name('body').send_keys(' ')
        await self.volume(self.settings['volume'])
        self.find_element_by_tag_name('body').send_keys(' ')
        return True

    async def pause(self) -> bool:
        if self.state != 'video':
            return False
        self.find_element_by_tag_name('body').send_keys(' ')
        return True
    
    async def volume(self, vol: int):
        if self.state != 'video':
            return False
        self.find_element_by_tag_name('body').send_keys(*([Keys.DOWN] * 10 + [Keys.UP] * vol)) # KalturaHB.videoObj.setVolume() doesn't work for some reason
        self.settings['volume'] = vol 
        return True

    async def seek(self, num: int):
        if self.state != 'video':
            return False
        currentTime = self.execute_script('return KalturaHB.videoObj.lastProperties.currentTime;')
        self.execute_script(f'KalturaHB.videoObj.seek({max(currentTime + num, 0)});')
        return True