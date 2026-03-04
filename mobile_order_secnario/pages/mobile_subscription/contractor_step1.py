# -*- coding: utf-8 -*-
import re
from pages.base_page import BasePage
from utils.locator_manager import locator_manager
from utils.logger import logger
from appium.webdriver.common.appiumby import AppiumBy


class ContractorStep1(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform)
        self.locs = locator_manager.get_locators("mobile_subscription")

    def input_customer_name_from_scenario(self, scenario_data):
        """시나리오 데이터에서 고객명을 가져와 입력"""
        customer_name = scenario_data['ContractorInfo']['fixed']['customer_name']
        self.wait_and_send_keys(self.locs['customer_name_input'], customer_name, "고객명 입력")

    def select_birth_date_logic(self, scenario_data):
        """법정생일 선택 (년도 스크롤 및 월/일 선택)"""
        birth_date = scenario_data['ContractorInfo']['fixed']['birth_date']
        year, month, day = birth_date.split('-')

        target_year = f"{year}년"
        target_month = f"{int(month)}월"
        target_day = str(int(day))

        # 생년월일 선택창(미선택) 클릭
        self.wait_and_click(self.locs['birth_date_select'], "법정생일 선택창 열기")

        if self.platform.lower() == 'android':
            self._select_birth_android(target_year, target_month, target_day)
        else:
            self._select_birth_ios(target_year, target_month, target_day)

    def _select_birth_android(self, year, month, day):
        """안드로이드: 지능형 스크롤로 년도 찾기 및 월/일 클릭"""
        logger.info(f"Android 스크롤 탐색 시작: {year}")

        max_attempts = 15
        for i in range(max_attempts):
            # 화면의 'N년' 요소들 수집
            elements = self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("년")')

            # 타겟 년도가 화면에 있는지 확인
            found = next((el for el in elements if el.text == year), None)
            if found:
                found.click()
                break

            # 현재 화면의 년도 범위 확인 (숫자만 추출)
            years_in_view = sorted(
                [int(re.sub(r'[^0-9]', '', e.text)) for e in elements if re.sub(r'[^0-9]', '', e.text)])
            target_int = int(re.sub(r'[^0-9]', '', year))

            if target_int < years_in_view[0]:
                # 타겟이 더 낮으면 아래로 스와이프 (과거로)
                self.driver.swipe(500, 500, 500, 800, 1000)
            else:
                # 타겟이 더 높으면 위로 스와이프 (미래로)
                self.swipe_up()

            if i == max_attempts - 1:
                raise Exception(f"년도 {year}를 찾을 수 없습니다.")

        # 월/일 선택 (텍스트 직접 매칭)
        self.wait_and_click({"android": {"xpath": f"//android.widget.TextView[@text='{month}']"}}, f"월({month}) 선택")
        self.wait_and_click({"android": {"xpath": f"//android.widget.TextView[@text='{day}']"}}, f"일({day}) 선택")

    def _select_birth_ios(self, year, month, day):
        """iOS: 로케이터 확정 전까지 공란 유지"""
        logger.warning("iOS 법정생일 선택 로직은 로케이터 확정 후 구현 예정입니다.")
        pass