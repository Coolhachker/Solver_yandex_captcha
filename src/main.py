import time
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
from selenium.common.exceptions import StaleElementReferenceException
from bypass_captcha import Solve
import os


class SolveCaptcha:
    def __init__(self):
        options = Options()
        # options.add_argument('user-agent=Mozilla/5.0 (Linux; Android 4.4.2; XMP-6250 Build/HAWK) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Safari/537.36 ADAPI/2.0 (UUID:9e7df0ed-2a5c-4a19-bec7-2cc54800f99d) RK3188-ADAPI/1.2.84.533 (MODEL:XMP-6250)')
        # options.add_experimental_option('mobileEmulation', {'deviceName': 'iPhone X'})
        chrome_driver = os.path.abspath('../yandexcaptcha/other_files/chromedriver')
        service = webdriver.ChromeService(executable_path=chrome_driver)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.window_width: int = 0
        self.window_height: int = 0
        self.action = ActionChains(self.driver)
        self.captcha = os.path.abspath('../yandexcaptcha/other_files/captcha.png')
        params = {
            'api': '',
            'captcha': self.captcha,
        }
        self.solver_captcha = Solve(**params)
        self.ignored_exceptions = (StaleElementReferenceException, )
        self.count_of_restart_solve_captcha: int = 0

    def run_solve(self):
        """
        Функция класса для запуска решения капчи. Содержит в себе другие функции класса для решения капчи. Все функции изолированы друг от друга.

        """
        try:
            self.get_main_page()
            self.bypass_first_captcha()
            self.solving_captcha(self.get_second_captcha)
            self.check_on_solve_captcha()
        finally:
            time.sleep(20)
            self.driver.quit()

    def get_main_page(self):
        """
        Функция получает основную страницу ya.ru.

        """
        self.driver.delete_all_cookies()
        self.driver.get('https://ya.ru')
        self.driver.maximize_window()
        self.window_width, self.window_height = self.driver.get_window_size()['width'], self.driver.get_window_size()['height']
        self.driver.delete_all_cookies()

    def bypass_first_captcha(self):
        """
        В функции реализован алгоритм решения первой капчи яндекс (обычная клик капча).

        """
        while True:
            try:
                fists_captcha = WebDriverWait(self.driver, 0).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="js-button"]')))
                self.action.move_to_element(fists_captcha).click().perform()
                break
            except Exception as ex:
                self.driver.refresh()

    def solving_captcha(self, second_captcha):
        """
        В функции реализован алгоритм решения smartcaptcha. -149 и -169 - это координаты смещения. Если капча не было успешно решена 3 раза, то скрпит начинает работу заново.

        :param second_captcha: webelement, который возращается из функции класса get_second_captcha.
        """
        if self.count_of_restart_solve_captcha != 3:
            dict_coordinates = self.solver_captcha.get_coordinates()
            for coordinate in dict_coordinates:
                try:
                    self.action.move_to_element_with_offset(second_captcha, -149 + coordinate['x'], -169 + coordinate['y']).click().perform()
                except StaleElementReferenceException:
                    continue
            button_for_moving_on_main_page = self.driver.find_element(By.XPATH, '//*[@id="advanced-captcha-form"]/div/div[3]/button[3]/div/span/span')
            self.action.move_to_element(button_for_moving_on_main_page).click().perform()
        else:
            self.count_of_restart_solve_captcha -= 3
            self.run_solve()

    @property
    def get_second_captcha(self):
        """
        В функции реализован алгоритм скачивания и обрезки капчи для сервиса решений капчи.

        :return: webelement second_captcha.
        """
        second_captcha = WebDriverWait(self.driver, 10, ignored_exceptions=self.ignored_exceptions).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="advanced-captcha-form"]')))
        self.driver.save_screenshot(self.captcha)
        Image.open(self.captcha).resize(self.check_on_screen_resolution).save(self.captcha)
        second_captcha_size = second_captcha.size
        #380, 811 - mobile size
        second_captcha_x = second_captcha.location['x']
        second_captcha_y = second_captcha.location['y']

        second_captcha_width = second_captcha_x + second_captcha_size['width']
        second_captcha_height = second_captcha_y + second_captcha_size['height']

        captcha_image_for_crop = Image.open(self.captcha)
        captcha_for_solve = captcha_image_for_crop.crop((second_captcha_x, second_captcha_y, second_captcha_width, second_captcha_height))
        captcha_for_solve.save(self.captcha)
        return second_captcha

    def check_on_solve_captcha(self):
        """
        Проверка на то, что капча была успешно пройдена.

        """
        try:
            WebDriverWait(self.driver, 5).until(ec.visibility_of_element_located((By.XPATH, '//*[@id="text"]')))
        except selenium.common.exceptions.TimeoutException:
            self.count_of_restart_solve_captcha += 1
            self.solving_captcha(self.get_second_captcha)

    @property
    def check_on_screen_resolution(self) -> tuple:
        screenshot = Image.open(self.captcha)
        if screenshot.size[0] < screenshot.size[1]:
            return 380, 811

        else:
            return self.window_width, self.window_height-130


if __name__ == '__main__':
    solve_captcha = SolveCaptcha()
    solve_captcha.run_solve()

