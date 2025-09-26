# -*- coding: utf-8 -*-

import pytest

# ➡️ 필요한 페이지 객체들을 모두 임포트
from pages.Order_docbar import MobileOrderPage
from pages.digitalsales_login import DigitalSalesLoginPage
from pages.order_status_completed import OrderStatusCompletedPage
from pages.Order_Status_page import OrderStatusPage
from utils.appium_driver import init_appium_driver
from utils.config_manager import ConfigManager
from utils.logger import logger
from pages.product_selection_page import ProductSelectionPage
from pages.auth_page import AuthPage


class TestMobileOrderScenario:
    """
    모바일 주문 시나리오에 대한 테스트 케이스를 포함하는 클래스입니다.
    """

    @pytest.fixture(scope="function")
    def driver_setup(self):
        """
        -> 테스트 함수마다 독립적인 Appium 드라이버를 생성하고 종료하는 fixture.
        """
        # -> Android 플랫폼으로 드라이버를 초기화합니다.
        appium_driver, platform = init_appium_driver(platform_name='Android')
        # -> 테스트 함수에서 사용할 수 있도록 driver와 platform 정보를 딕셔너리 형태로 반환합니다.
        yield {"driver": appium_driver, "platform": platform}
        # -> 테스트 함수가 끝나면 드라이버를 종료합니다.
        logger.info("Appium 드라이버를 종료합니다.")
        appium_driver.quit()

    def test_full_order_scenario(self, driver_setup):
        """
        -> 로그인부터 고객 인증까지 전체 시나리오를 테스트합니다.
        """
        logger.info("🚀 모바일 주문 전체 시나리오 테스트를 시작합니다.")
        try:
            appium_driver = driver_setup["driver"]
            platform = driver_setup["platform"]
            config_manager = ConfigManager()
            test_data = config_manager.get_test_data()
            user_data = test_data["UserData"]
            customer_data = test_data["CustomerData"]
            product_data = test_data["ProductData"]

            # 1. 로그인 단계
            login_page = DigitalSalesLoginPage(appium_driver, platform)
            login_page.login(user_data["VALID_INDIVIDUAL_ID"], user_data["VALID_INDIVIDUAL_PASSWORD"])

            # 2. 모바일 주문 서비스 이동 단계
            order_page = MobileOrderPage(appium_driver, platform)
            order_page.access_mobile_order_via_docbar()
            # order_page.start_general_order()    #일반 주문하기 진입
            order_page.start_general_count()   #주문 이어하기 통해 주문 현황 진입
            #
            # # 3. 고객 인증 단계
            # auth_page = AuthPage(appium_driver, platform)
            # auth_page.perform_customer_authentication(
            #     customer_type=customer_data["VALID_CUSTORMER_TYPE"],
            #     name=customer_data["VALID_CUSTORMER_NAME"],
            #     phone_number=customer_data["VALID_CUSTORMER_PHONE"]
            # )
            #
            # # 4. 주문현황 상태 확인(인증입력)
            # order_status_page = OrderStatusPage(appium_driver, platform)
            # order_status_page.verify_auth_button_for_customer(
            #     customer_name=customer_data["VALID_CUSTORMER_NAME"]
            #)
            #TODO:PASS앱 인증 함수 생성 필요

            #6. 주문현황 상태 확인(인증완료)
            order_status_completed_page = OrderStatusCompletedPage(appium_driver, platform)
            order_status_completed_page.send_input_customer(
                customer_name=customer_data["VALID_CUSTORMER_NAME"]
            )
            order_status_completed_page.click_auth_completed_for_customer(
                customer_name=customer_data["VALID_CUSTORMER_NAME"]
            )
            # 주문 이어서 하기 클릭
            order_status_completed_page.click_order_continue()

            # 7. 상품 선택 페이지 시나리오
            product_page = ProductSelectionPage(appium_driver, platform)
            product_page.search_product(product_data["product_name"]) # 제품 검색
            product_page.select_first_product(product_data["product_name"]) #첫번째 제품 선택
            #TODO : 현재는 랜덤으로 판매구분 선택하지만 나중엔 GCP연동해서 판매구분 받아오고 판매 구분에 따라 step3까지 분기 처리 필요
            product_page.select_sale_type_randomly() #하위 판매구분 하위 속성 중 랜덤 선택
            product_page.select_management_type_randomly()  #관리 유형이 노출되면 랜덤 선택
            product_page.select_mandatory_period_randomly() # 의무 사용 기간이 노출되면 랜덤 선택
            product_page.select_separate_product_randomly() #별매 상품 랜덤 선택
            product_page.additional_server_buttons_randomly()   #부가서비스 랜덤 선택
            product_page.containing_goods() #상품 담기
            #TODO : 다건 주문에 대한 고려 필요 GCP연동 시 시나리오 탭 읽어와서 다건 주문할지 단건 주문할지에 따라 분기 처리
            #product_page.adding_goods() #상품 추가하기(다건 주문시 필요)
            product_page.enter_discount_information()   #할인정보 입력 클릭(step3이동)

            # 8. 할인 선택 페이지 시나리오


        #     logger.info("✅ 모바일 주문 전체 시나리오 테스트가 성공적으로 완료되었습니다.")
        #
        except Exception as e:
            # -> 테스트 실패 시 로그를 남기고 pytest를 통해 테스트를 실패 처리합니다.
            logger.error(f"❌ 모바일 주문 전체 시나리오 테스트 실패: {e}", exc_info=True)
            pytest.fail(str(e))
