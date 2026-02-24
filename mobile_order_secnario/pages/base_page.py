# -*- coding: utf-8 -*-
# -> 필요한 모듈들을 모두 임포트합니다.
import os
import time
import random
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
        -> id, xpath, accessibility_id를 모두 반환하여, 로케이터 데이터(딕셔너리나 문자열)를 코드가 
        이해할 수 있는 형태(튜플 리스트)로 변환(find_element_with_fallback함수에서만 활용)
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

    def find_element_with_fallback(self, locator, timeout=5):
        """
        여러 로케이터 전략을 순차적으로 시도하여 요소를 찾는 함수.
        반드시 있어야 하는 요소를 찾고 없으면 에러를 발생시키는 함수.
        timeout(5초)까지 찾고 없으면 스킵

        :param locator: 로케이터 딕셔너리
        :param timeout: 대기 시간 (기본값 5초)
        :return: 찾은 WebElement 객체
        """
        last_exception = None
        try:
            # _get_locator_tuples 함수로 로케이터 튜플 목록을 가져옵니다.
            locator_tuples = self._get_locator_tuples(locator)
        except ValueError as e:
            logger.error(f"유효하지 않은 로케이터: {locator}. 요소를 찾을 수 없습니다.")
            raise e

        # 각 로케이터 튜플을 순서대로 시도합니다.
        # by : ID, XPATH 등 선택
        # value : 로케이터 값
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

    def get_all_elements_with_fallback(self, locator):
        """
        [추가] 로케이터(JSON)를 받아서, 현재 플랫폼에 맞는 '모든' 요소를 찾아서 리스트로 반환합니다.
        (get_all_elements)
        
        :param locator: {'android': {...}, 'ios': {...}} 형태의 딕셔너리
        :return: 찾은 WebElement 리스트 (없으면 빈 리스트 [])

        find_element_with_fallback는 찾고자 하는 요소가 없으면 에러 발생
        get_all_elements_with_fallback는 요소를 전체 확인 후, 리스트 형태로 반환(없으면 빈 요소 반환)
        """
        try:
            # 1. 내부 함수를 통해 현재 플랫폼에 맞는 전략(By, Value)만 뽑아옵니다.
            locator_tuples = self._get_locator_tuples(locator)
            
            # 2. 뽑아온 전략으로 find_elements(복수형) 실행
            for by, value in locator_tuples:
                elements = self.driver.find_elements(by, value)
                
                # 하나라도 찾았으면 그 리스트 반환
                if elements:
                    return elements
            
            # 아무것도 못 찾았으면 빈 리스트 반환
            return []
            
        except Exception as e:
            # 로그는 선택 사항
            return []

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
                # 클릭 시도
                element.click()
                # 클릭이 성공적으로 실행되었을 때만 로그 출력
                logger.info(f"✅ '{element_name}' 요소를 클릭했습니다. (전략: {by})")
                return
            except (TimeoutException, NoSuchElementException) as e:
                logger.warning(f"'{by}:{value}' 전략으로 '{element_name}' 클릭 실패. 재시도합니다.")
                last_exception = e
            except Exception as e:
                # 클릭 관련 예외 (WebDriverException 등) 처리
                logger.error(f"❌ '{element_name}' 클릭 중 예외 발생: {e}")
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
                # [중요] 일부 입력창(특히 WebView 내 EditText)은 클릭(포커스) 후에만 입력이 정상 동작합니다.
                try:
                    element.click()
                except Exception:
                    pass
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

    def swipe_up(self, start_y_ratio=0.7, end_y_ratio=0.2, duration=800):
        """
        [추가] 화면을 아래에서 위로 스와이프하는 범용 함수입니다.
        :param start_y_ratio: 스와이프 시작 Y좌표 비율 (화면 높이 대비)
        :param end_y_ratio: 스와이프 종료 Y좌표 비율 (화면 높이 대비)
        :param duration: 스와이프 동작 시간 (ms)
        """
        try:
            size = self.driver.get_window_size()
            start_x = size['width'] / 2
            start_y = size['height'] * start_y_ratio
            end_y = size['height'] * end_y_ratio

            self.driver.swipe(start_x, start_y, start_x, end_y, duration)

        except Exception as e:
            logger.error(f"❌ 스와이프 실패: {e}", exc_info=True)
            raise

    def swipe_down(self, start_y_ratio=0.2, end_y_ratio=0.7, duration=800):
        """
        [추가] 화면을 위에서 아래로 스와이프하는 범용 함수입니다.
        :param start_y_ratio: 스와이프 시작 Y좌표 비율 (화면 높이 대비)
        :param end_y_ratio: 스와이프 종료 Y좌표 비율 (화면 높이 대비)
        :param duration: 스와이프 동작 시간 (ms)
        """
        try:
            size = self.driver.get_window_size()
            start_x = size['width'] / 2
            start_y = size['height'] * start_y_ratio
            end_y = size['height'] * end_y_ratio

            self.driver.swipe(start_x, start_y, start_x, end_y, duration)

        except Exception as e:
            logger.error(f"❌ 스와이프 실패: {e}", exc_info=True)
            raise

    def select_random_option(self, locator_info, element_name):
        """
        요소를 찾아 무작위로 하나를 선택하고 클릭하는 함수입니다.
        :param locator_info: 로케이터 정보 (딕셔너리 형태)
        :param element_name: 요소의 이름 (로그 출력용)
        """
        logger.info(f"'{element_name}' 목록에서 랜덤 선택 시도.")
        try:
            locator_tuples = self._get_locator_tuples(locator_info)
            # EC.presence_of_all_elements_located를 사용하여 요소 목록이 나타날 때까지 대기
            elements = self.wait.until(EC.presence_of_all_elements_located(locator_tuples[0]))

            if not elements:
                # 목록을 찾았으나 비어있는 경우, 찾지 못한 것으로 간주
                raise NoSuchElementException(f"'{element_name}' 목록을 찾았으나 요소가 비어있습니다.")

            random_element = random.choice(elements)

            # [FIX: StaleElementReferenceException] 클릭 전에 텍스트를 미리 저장
            # 클릭 후 DOM이 변경되면 요소가 "Stale"해지므로 텍스트를 미리 가져옵니다.
            selected_text = random_element.text

            random_element.click()

            logger.info(f"✅ '{selected_text}'을(를) 랜덤으로 선택하여 클릭 완료.")
            self.short_sleep()
            return selected_text # 선택한 값 반환

        except (TimeoutException, NoSuchElementException) as e:
            # 요소를 찾지 못하면 바로 예외 발생 (재시도하지 않음)
            logger.error(f"❌ {element_name} 선택 실패: {e}", exc_info=True)
            self.take_screenshot(f"{element_name.replace(' ', '_')}_selection_failure")
            raise

    def check_element_exists(self, locator, timeout=3):
        """
        특정 요소가 화면에 존재하는지 확인(fallback함수와 달리 에러를 발생시키지 않음)
        분기 처리에 요소가 있는지 확인
        :param locator: 로케이터 딕셔너리
        :param timeout: 확인 대기 시간 (초)
        :return: True(존재함) / False(없음)
        """
        try:
            locator_tuples = self._get_locator_tuples(locator)
            # 짧은 시간만 대기하도록 설정
            wait = WebDriverWait(self.driver, timeout)
            
            for by, value in locator_tuples:
                try:
                    # 요소가 존재하는지 확인
                    wait.until(EC.presence_of_element_located((by, value)))
                    return True
                except TimeoutException:
                    continue
            return False
        except Exception:
            return False

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
