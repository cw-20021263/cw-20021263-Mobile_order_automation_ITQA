# -*- coding: utf-8 -*-
from pages.base_page import BasePage
from utils.locator_manager import locator_manager
from utils.logger import logger


class SubscriptionPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform)
        # locator_manager를 통해 플랫폼에 맞는 로케이터 로드
        self.locs = locator_manager.get_locators("mobile_subscription")

    def execute_step1_contractor(self, data):
        """STEP 1: 계약자 정보 입력 (시트 기반)"""
        logger.info("--- STEP 1 시작: 계약자 정보 ---")
        self.wait_and_send_keys(self.locs['step1']['name_input'], data['customer_name'], "고객명")
        self.wait_and_send_keys(self.locs['step1']['phone_input'], data['phone'], "휴대폰번호")

        # 시트에 주소 유형이 정의되어 있으므로 해당 텍스트를 찾아 클릭 (유연한 선택 적용 가능)
        # 만약 고정 로케이터가 없다면 BasePage의 select_random_option을 응용 가능
        self.wait_and_click({"xpath": f"//*[@text='{data['address_type']}']"}, data['address_type'])
        logger.info(f"주소 입력 완료: {data['address_main']}")

    def execute_step2_install(self, data):
        """STEP 2: 설치 정보 입력 (시트 기반)"""
        logger.info("--- STEP 2 시작: 설치 정보 ---")
        self.wait_and_send_keys(self.locs['step2']['address_input'], data['install_address'], "설치주소")
        self.wait_and_send_keys(self.locs['step2']['memo_input'], data['install_memo'], "설치메모")
        # 날짜 선택 등은 캘린더 위젯 대응 로직 필요

    def execute_step3_payment(self, data):
        """STEP 3: 결제 정보 입력 (랜덤 및 고정 혼합)"""
        logger.info("--- STEP 3 시작: 결제 정보 ---")
        if data['payment_method'] == "카드이체":
            self.wait_and_send_keys(self.locs['step3']['card_input'], data['card_number'], "카드번호")
            # 만약 카드사를 랜덤으로 선택하고 싶다면?
            # selected_card = self.select_random_option(self.locs['step3']['card_list'], "카드사 목록")
            # logger.info(f"랜덤 선택된 카드사: {selected_card}")
        else:
            self.wait_and_send_keys(self.locs['step3']['bank_select'], data['card_company'], "은행명")