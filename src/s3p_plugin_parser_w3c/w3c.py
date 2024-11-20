import datetime
import time

from s3p_sdk.plugin.payloads.parsers import S3PParserBase
from s3p_sdk.types import S3PRefer, S3PDocument, S3PPlugin
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class W3C(S3PParserBase):
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """

    SOURCE_NAME = 'w3c'
    _content_document: list[S3PDocument]
    HOST = 'https://www.w3.org/TR/'

    def __init__(self, refer: S3PRefer, plugin: S3PPlugin, web_driver: WebDriver, max_count_documents: int = None,
                 last_document: S3PDocument = None):
        super().__init__(refer, plugin, max_count_documents, last_document)

        # Тут должны быть инициализированы свойства, характерные для этого парсера. Например: WebDriver
        self._driver = web_driver
        self._wait = WebDriverWait(self._driver, timeout=20)

    def _parse(self):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self.HOST}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -
        self._driver.get('https://www.w3.org/TR/')
        doc_list = self._driver.find_elements(By.CLASS_NAME, 'tr-list__item__header')
        for doc in doc_list:

            # Ссылка на документ
            __doc_link = doc.find_element(By.TAG_NAME, 'a').get_attribute('href')

            try:
                __title = doc.find_element(By.TAG_NAME, 'a').text
            except:
                # завершение обработки документа, переход к следующему
                self.logger.exception(f'Ошибка при обработке документа {__doc_link}')
                self._driver.close()
                self._driver.switch_to.window(self._driver.window_handles[0])
                continue


            # pub_date
            __pub_date = datetime.datetime.strptime(doc.find_element(By.XPATH, '..//time').get_attribute('datetime'), '%Y-%m-%d')

            # tags
            tags_el = doc.find_elements(By.XPATH, '..//*[contains(text(), \'Tags\')]/../dd')
            __tags = [x.text for x in tags_el]

            # deliverers (workgroup)
            deliverers_el = doc.find_elements(By.XPATH, '..//*[contains(text(), \'Deliverers\')]/../dd')
            __devilverers = [x.text for x in deliverers_el]

            # family
            __family = doc.find_element(By.XPATH, '../../h2').text

            self._driver.execute_script("window.open('');")
            self._driver.switch_to.window(self._driver.window_handles[1])
            self._driver.get(__doc_link)
            time.sleep(0.5)

            # abstract
            try:
                __abstract = self._driver.find_element(By.ID, 'abstract').text
            except:
                # Удален np.nan
                __abstract = None

            # text_content
            __text_content = self._driver.find_element(By.TAG_NAME, 'body').text

            # web_link
            try:
                __web_link = self._driver.find_element(By.XPATH,
                                                    '//dt[contains(text(), \'This version\')]/following-sibling::dd[1]//a').get_attribute(
                    'href')
            except:
                self.logger.exception(
                    f'Не удалось получить веб-ссылку на версию документа за определенную дату. В web_link вносится общая ссылка {__doc_link}')
                __web_link = __doc_link

            # doc_type
            try:
                __doc_type = self._driver.find_element(By.XPATH, '//p[@id = \'w3c-state\']/a').text
            except:
                # удален np.nan
                __doc_type = None

            # authors
            authors_el = self._driver.find_elements(By.XPATH,
                                                   '//dt[contains(text(), \'Authors\')]/following-sibling::dd[@class=\'editor p-author h-card vcard\']')
            __authors = [x.text for x in authors_el]

            # authors
            editors_el = self._driver.find_elements(By.XPATH,
                                                   '//dt[contains(text(), \'Editors\')]/following-sibling::dd[@class=\'editor p-author h-card vcard\']')
            __editors = [x.text for x in editors_el]

            # commit
            commit_links = self._driver.find_elements(By.XPATH, '//a[contains(text(), \'Commit history\')]')
            if len(commit_links) > 0:
                self._driver.get(commit_links[0].get_attribute('href'))
                time.sleep(1)
                commit_el = self._driver.find_elements(By.XPATH,
                                                      '//div[@class=\'TimelineItem TimelineItem--condensed pt-0 pb-2\']//p[contains(@class,\'mb-1\')]')
                __commits = [x.text for x in commit_el]
            else:
                # удален np.nan
                __commits = None

            spp_doc = S3PDocument(
                id=None,
                title=__title,
                abstract=__abstract,
                text=__text_content,
                link=__web_link,
                storage=None,
                other={
                    'doc_type': __doc_type,
                    'devilverers': __devilverers,
                    'authors': __authors,
                    'tags': __tags,
                    'commits': __commits,
                    'family': __family,
                    'editors': __editors,
                },
                published=__pub_date,
                loaded=None,
            )

            self._find(spp_doc)

            self._driver.close()
            self._driver.switch_to.window(self._driver.window_handles[0])

        # ---
        # ========================================
        ...
