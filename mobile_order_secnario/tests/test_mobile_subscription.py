# -*- coding: utf-8 -*-
import pytest
from pages.subscription_page import SubscriptionPage
from pages.digitalsales_login import DigitalSalesLoginPage
import json


def test_chungyak_scenario(driver, platform):
    # 1. 데이터 로드
    with open('data/test_data.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)

    scenario = test_data['Scenarios'][0]  # 첫 번째 시나리오 (이희운)

    # 2. 로그인 (기존 코드 활용)
    login_page = DigitalSalesLoginPage(driver, platform)
    login_page.login(test_data['CommonConfig']['login_id'], test_data['CommonConfig']['login_pw'])

    # 3. 청약 프로세스 진입
    sub_page = SubscriptionPage(driver, platform)

    # STEP 1 ~ 3 실행
    sub_page.execute_step1_contractor(scenario['Step1_CustomerInfo'])
    sub_page.short_sleep()

    sub_page.execute_step2_install(scenario['Step2_InstallInfo'])
    sub_page.short_sleep()

    sub_page.execute_step3_payment(scenario['Step3_PaymentInfo'])

    logger.info("청약 데이터 입력 완료 (STEP 3까지)")