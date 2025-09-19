# -*- coding: utf-8 -*-
# -> 필요한 모듈들을 모두 임포트합니다.
import os
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils.logger import logger


class BasePage:
    def __init__(self, driver, platform):
        self.driver = driver
        # -> platform 값이 없을 경우를 대비하여 기본값을 설정합니다.
        self.platform = platform.lower() if platform else 'android'
        # -> 기본 대기 시간을 10초로 늘려 안정성을 높입니다.
        self.wait = WebDriverWait(self.driver, 10)

    def _get_locator_tuples(self, locator):
        """
        -> id, xpath, accessibility_id를 모두 반환하여, 순차적으로 시도할 수 있도록 로케이터 '튜플 리스트'를 반환합니다.
        """
        # -> locator가 None이거나 비어있는 dict일 경우 에러를 발생시킵니다.
        if not locator or (isinstance(locator, dict) and not any(locator.values())):
            raise ValueError("로케이터 값이 유효하지 않습니다.")

        locators = []
        if isinstance(locator, dict):
            # -> ID가 있으면 최우선으로 추가합니다.
            if locator.get('id'):
                locators.append((AppiumBy.ID, locator['id']))
            # -> XPath가 있으면 다음 순서로 추가합니다.
            if locator.get('xpath'):
                locators.append((AppiumBy.XPATH, locator['xpath']))
            # -> accessibility_id가 있으면 마지막으로 추가합니다.
            if locator.get('accessibility_id'):
                locators.append((AppiumBy.ACCESSIBILITY_ID, locator['accessibility_id']))
        # -> locator가 문자열일 경우 처리 방식을 추가합니다.
        elif isinstance(locator, str):
            if locator.startswith('//'):
                locators.append((AppiumBy.XPATH, locator))
            else:
                # -> 기본적으로 accessibility_id로 시도하도록 설정합니다.
                locators.append((AppiumBy.ACCESSIBILITY_ID, locator))

        if not locators:
            raise ValueError(f"지원되지 않거나 유효하지 않은 로케이터 형식입니다: {locator}")

        return locators

    def find_element_with_fallback(self, locator):
        """
        -> 여러 로케이터 전략을 순차적으로 시도하여 요소를 찾는 함수입니다.
        """
        last_exception = None
        try:
            # _get_locator_tuples 함수로 로케이터 튜플 목록을 가져옵니다.
            locator_tuples = self._get_locator_tuples(locator)
        except ValueError as e:
            logger.error(f"유효하지 않은 로케이터: {locator}. 요소를 찾을 수 없습니다.")
            raise e

        # 각 로케이터 튜플을 순서대로 시도합니다.
        for by, value in locator_tuples:
            try:
                # 요소의 존재(presence) 여부를 확인합니다.
                element = self.wait.until(EC.presence_of_element_located((by, value)))
                logger.info(f"✅ '{by}:{value}' 전략으로 요소를 발견했습니다.")
                return element
            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"'{by}:{value}' 전략으로 요소 찾기 실패. 다음 전략으로 재시도합니다.")
                last_exception = e

        # 모든 시도가 실패하면 예외를 발생시킵니다.
        logger.error(f"모든 로케이터 전략으로 요소를 찾을 수 없습니다: {locator}")
        self.take_screenshot("find_element_failure")
        raise TimeoutException(f"요소를 찾을 수 없습니다. (로케이터: {locator})", screen=getattr(last_exception, 'screen', None),
                               stacktrace=getattr(last_exception, 'stacktrace', None))

    def wait_and_click(self, locator, element_name, timeout=10):
        """
        -> id, xpath 등 여러 전략으로 요소를 찾아 클릭하는 함수로 개선합니다.
        """
        last_exception = None
        try:
            # -> locator가 유효한지 먼저 확인합니다.
            locator_tuples = self._get_locator_tuples(locator)
        except ValueError as e:
            logger.warning(f"'{element_name}'에 대한 로케이터 값이 유효하지 않아 클릭을 건너뜁니다.")
            # -> 에러를 다시 발생시켜 테스트가 실패하도록 합니다.
            raise e

        for by, value in locator_tuples:
            try:
                wait = WebDriverWait(self.driver, timeout)
                # -> EC.element_to_be_clickable을 사용하여 클릭 가능한 상태까지 기다립니다.
                element = wait.until(EC.element_to_be_clickable((by, value)))
                element.click()
                logger.info(f"'{element_name}' 요소를 클릭했습니다. (전략: {by})")
                return
            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"'{by}:{value}' 전략으로 '{element_name}' 클릭 실패. 재시도합니다.")
                last_exception = e

        logger.error(f"모든 전략으로 '{element_name}' 요소를 클릭하지 못했습니다: {locator}")
        self.take_screenshot(f"{element_name.replace(' ', '_')}_click_failure")
        raise TimeoutException(f"'{element_name}' 요소를 찾거나 클릭할 수 없습니다.", screen=getattr(last_exception, 'screen', None),
                               stacktrace=getattr(last_exception, 'stacktrace', None))

    def wait_and_send_keys(self, locator, text, element_name, timeout=10):
        """
        -> id, xpath 등 여러 전략으로 요소를 찾아 텍스트를 입력하는 함수로 개선합니다.
        """
        last_exception = None
        try:
            locator_tuples = self._get_locator_tuples(locator)
        except ValueError as e:
            logger.error(f"'{element_name}'에 대한 로케이터 값이 유효하지 않습니다.")
            raise e

        for by, value in locator_tuples:
            try:
                wait = WebDriverWait(self.driver, timeout)
                # -> EC.visibility_of_element_located를 사용하여 요소가 보일 때까지 기다립니다.
                element = wait.until(EC.visibility_of_element_located((by, value)))
                element.clear()
                element.send_keys(text)
                logger.info(f"'{element_name}' 요소에 텍스트 '{text}'를 입력했습니다. (전략: {by})")
                return
            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"'{by}:{value}' 전략으로 '{element_name}'에 텍스트 입력 실패. 재시도합니다.")
                last_exception = e

        logger.error(f"모든 전략으로 '{element_name}' 요소에 텍스트를 입력하지 못했습니다: {locator}")
        self.take_screenshot(f"{element_name.replace(' ', '_')}_input_failure")
        raise TimeoutException(f"'{element_name}' 요소를 찾거나 입력할 수 없습니다.", screen=getattr(last_exception, 'screen', None),
                               stacktrace=getattr(last_exception, 'stacktrace', None))

    def take_screenshot(self, name):
        # -> 스크린샷 저장 로직을 안정적으로 수정합니다.
        try:
            # -> 프로젝트 루트 경로를 올바르게 찾도록 수정합니다.
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            screenshot_dir = os.path.join(project_root, 'reports', 'screenshots')
            os.makedirs(screenshot_dir, exist_ok=True)
            # -> 파일 이름에 시간값을 추가하여 중복을 방지합니다.
            file_path = os.path.join(screenshot_dir, f"{name}_{time.time()}.png")
            self.driver.save_screenshot(file_path)
            logger.info(f"스크린샷 저장 완료: {file_path}")
        except WebDriverException as e:
            logger.error(f"스크린샷 저장 실패: {e}")

    def short_sleep(self):
        time.sleep(1)

    def medium_sleep(self):
        time.sleep(3)

    def long_sleep(self):
        time.sleep(5)

    def hide_keyboard(self):
        try:
            self.driver.hide_keyboard()
            logger.info("키보드를 숨겼습니다.")
        except WebDriverException:
            # -> 키보드가 없어도 오류가 발생하지 않도록 pass 처리합니다.
            pass
