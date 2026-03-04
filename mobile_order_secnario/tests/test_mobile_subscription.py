# -*- coding: utf-8 -*-
import pytest
import json
import os
from pages.mobile_subscription.subscription_main_page import SubscriptionMainPage
from pages.digitalsales_login import DigitalSalesLoginPage
from utils.logger import logger


def test_run_mobile_subscription(driver, platform):
    """
    모바일 청약 주문 자동화 실행 스크립트
    """
    # 1. 테스트 데이터 로드 (scenarios_data.json)
    data_path = os.path.join(os.getcwd(), 'data', 'scenarios_data.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    # 첫 번째 시나리오 데이터 선택
    scenario = all_data['ChungyakScenarios'][0]
    logger.info(f"🚀 테스트 시작 시나리오: {scenario['scenario_id']}")

    # 2. 로그인 수행
    login_page = DigitalSalesLoginPage(driver, platform)
    login_page.login("CWDS#MCL78", "Test1234!")  # 실제 테스트 계정 정보

    # 3. 메인 통합 페이지 인스턴스 생성 및 프로세스 시작
    # SubscriptionMainPage 내부에서 Step1의 함수들을 순서대로 호출합니다.
    main_order_page = SubscriptionMainPage(driver, platform)

    try:
        # STEP 1부터 순차적으로 실행
        main_order_page.run_mobile_order_process(scenario)

    except Exception as e:
        logger.error(f"❌ 테스트 중 오류 발생: {str(e)}")
        main_order_page.save_screenshot("subscription_error")
        raise e

    logger.info("🎉 모든 주문 입력 프로세스가 정상적으로 종료되었습니다.")