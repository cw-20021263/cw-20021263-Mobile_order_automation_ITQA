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
from pages.discount_selection_page import DiscountSelectionPage
from pages.step4_payment_info import Step4PaymentInfoPage

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
            payment_data = test_data["PaymentData"]

            # 1. 로그인 단계
            login_page = DigitalSalesLoginPage(appium_driver, platform)
            login_page.login(user_data["VALID_INDIVIDUAL_ID"], user_data["VALID_INDIVIDUAL_PASSWORD"])

            # 2. 모바일 주문 서비스 이동 단계
            order_page = MobileOrderPage(appium_driver, platform)
            order_page.access_mobile_order_via_docbar()  # Docbar로 모바일 주문 진입
            #order_page.start_general_order()             #일반 주문하기 진입
            order_page.start_general_count()            #주문 이어하기 통해 주문 현황 진입
            #
            # 3. 고객 인증(고입확)
            # auth_page = AuthPage(appium_driver, platform)
            # auth_page.perform_customer_authentication(
            #     customer_type=customer_data["VALID_CUSTORMER_TYPE"],
            #     name=customer_data["VALID_CUSTORMER_NAME"],
            #     phone_number=customer_data["VALID_CUSTORMER_PHONE"]
            # )
            
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

            # 7. 상품 선택(Step2) 페이지 시나리오
            product_page = ProductSelectionPage(appium_driver, platform)
            product_page.search_product(product_data["product_name"]) # 제품 검색
            product_page.select_first_product(product_data["product_name"]) #첫번째 제품 선택
            #TODO : 현재는 랜덤으로 판매구분 선택하지만 나중엔 GCP연동해서 판매구분 받아오고 판매 구분에 따라 step3까지 분기 처리 필요
            product_page.select_sale_type_randomly()            #하위 판매구분 하위 속성 중 랜덤 선택
            product_page.select_management_type_randomly()      #관리 유형이 노출되면 랜덤 선택
            product_page.select_mandatory_period_randomly()     # 의무 사용 기간이 노출되면 랜덤 선택
            product_page.select_separate_product_randomly()     #별매 상품 랜덤 선택
            product_page.additional_server_buttons_randomly()   #부가서비스 랜덤 선택
            product_page.containing_goods()                     #상품 담기
            #TODO : 다건 주문에 대한 고려 필요 GCP연동 시 시나리오 탭 읽어와서 다건 주문할지 단건 주문할지에 따라 분기 처리
            #product_page.adding_goods() #상품 추가하기(다건 주문시 필요)
            PRODUCT_COUNT = 1   # 제품 n개 선택할 때 변수로서 일단은 1로 하드코딩 TODO : 추후 step2에서 선택한 수만큼 추가 필요
            product_page.enter_discount_information()   #할인정보 입력 클릭(step3이동)

            # 8. 할인 선택(Step3) 페이지 시나리오
            discount_page = DiscountSelectionPage(appium_driver, platform)
            discount_page.verify_page_components(
                expected_customer_name=customer_data["VALID_CUSTORMER_NAME"],
                expected_total_count=PRODUCT_COUNT)
            discount_page.check_simultaneous_discount(product_count=PRODUCT_COUNT)
            discount_page.check_and_configure_combination_discount()
            discount_page.get_regular_payment_discount()
            discount_page.get_prepass_discount()
            discount_page.get_rental_fee_agreement_discount()
            discount_page.select_prepayment_discount_option()
            #discount_page.check_and_select_prepayment2_discount()
            #TODO: 선납할인, 선납할인2 중복적용 불가로 랜덤으로 둘 중하나 선택할 수 있도록 코드 변경 필요
            discount_page.verify_price_calculation_logic()
            #TODO : 제품을 2개이상 선택했을 때 할인선택 등 하는 것 작업 필요
            discount_page.click_next_button()

            #9 결제정보 입력(step4) 페이지 시나리오
            step4_page = Step4PaymentInfoPage(appium_driver, platform)
             # 2. 페이지 진입 확인 및 세부 텍스트 검증
            step4_page.verify_page_compoenets(expected_customer_name=customer_data["VALID_CUSTORMER_NAME"])
            # 3. 결제 금액 정보 확인(정기결제, 수납금액)
            step4_page.check_payment_amounts()
            # 4. 정기결제 수단 선택 및 추가
            step4_page.regular_payment_method_selection(payment_data, customer_name=customer_data["VALID_CUSTORMER_NAME"])
            # 5. 수납결제 수단 선택 및 추가
            step4_page.lump_sum_payment_method_selection(payment_data, customer_name=customer_data["VALID_CUSTORMER_NAME"])
            # 6. 다음 버튼 클릭
            step4_page.click_next_button()
            
            #10 설치정보 입력(step5) 페이지 시나리오


            logger.info("✅ 모바일 주문 전체 시나리오 테스트가 성공적으로 완료되었습니다.")
        
        except Exception as e:
            # -> 테스트 실패 시 로그를 남기고 pytest를 통해 테스트를 실패 처리합니다.
            logger.error(f"❌ 모바일 주문 전체 시나리오 테스트 실패: {e}", exc_info=True)
            pytest.fail(str(e))

    def test_step5_only_exec(self, driver_setup):
        """
        [디버깅용] Step 4 결제정보 선택 화면 테스트
        - pytest -k test_step4_only_exec 명령어로 실행
        """
        import time
        try:
            driver = driver_setup["driver"]
            platform = driver_setup["platform"]

            config_manager = ConfigManager()
            test_data = config_manager.get_test_data()
            customer_data = test_data["CustomerData"]
            payment_data = test_data["PaymentData"]

            logger.info("🚀 [Step 4] 결제정보 선택 화면 디버깅 시작")
            
            # 1. 페이지 객체 생성
            step4_page = Step4PaymentInfoPage(driver, platform)
            
            # 2. 페이지 진입 확인 및 타이틀 검증
            time.sleep(1)
            driver.press_keycode(4)  # Android KEYCODE_BACK
            time.sleep(2)
            # step4_page.verify_page_compoenets(
            #     expected_customer_name=customer_data["VALID_CUSTORMER_NAME"]
            # )
            
            # 3. 결제 금액 정보 로깅 (금액이 잘 뜨는지 확인)
            #step4_page.check_payment_amounts()
            
            step4_page.regular_payment_method_selection(payment_data, 
            customer_name=customer_data["VALID_CUSTORMER_NAME"])

            logger.info("✅ [Step 4] 디버깅 완료")

        except Exception as e:
            logger.error(f"❌ [Step 4] 테스트 실패: {e}", exc_info=True)
            pytest.fail(str(e))