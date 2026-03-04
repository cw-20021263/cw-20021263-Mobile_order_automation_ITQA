# -*- coding: utf-8 -*-
from pages.base_page import BasePage
from pages.mobile_subscription.contractor_step1 import ContractorStep1
from utils.logger import logger


class SubscriptionMainPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform)
        # 각 스텝별 클래스 인스턴스 초기화
        self.step1 = ContractorStep1(driver, platform)

    def run_mobile_order_process(self, scenario_data):
        """
        모바일 주문 전체 프로세스 실행 (STEP 1 ~ STEP 6)
        """
        logger.info("========== 모바일 주문 자동화 프로세스 시작 ==========")

        # [STEP 1] 계약자 정보 입력
        self.execute_step1_process(scenario_data)

        # [STEP 2 ~ 6] 향후 구현 시 추가
        # self.step2.execute_step2(...)

        logger.info("========== 모든 주문 단계 완료 ==========")

    def execute_step1_process(self, scenario_data):
        """STEP 1: 계약자 정보 입력 및 본인인증 단계 실행"""
        logger.info(">>> [STEP 1] 계약자 정보 입력 단계 시작")

        # 1. 고객명 입력 (scenarios_data.json 활용)
        self.step1.input_customer_name_from_scenario(scenario_data)

        # 2. 법정생일 선택 (스크롤 로직 포함)
        self.step1.select_birth_date_logic(scenario_data)

        logger.info(">>> [STEP 1] 완료")