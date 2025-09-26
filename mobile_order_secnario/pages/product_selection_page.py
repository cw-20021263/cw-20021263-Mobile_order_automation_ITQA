# pages/product_selection_page.py

from pages.base_page import BasePage
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.locator_manager import locator_manager
from utils.logger import logger


class ProductSelectionPage(BasePage):
    """
    상품 검색, 판매 구분, 관리 유형, 의무 사용 기간을 선택하는 페이지 객체입니다.
    """

    def __init__(self, driver, platform):
        super().__init__(driver, platform)
        # -> 플랫폼 설정 및 'product_select' 로케이터 그룹 로드
        locator_manager.set_platform(platform)
        self.locators = locator_manager.get_locators("product_select")

    def search_product(self, product_name): #제품 선택(product_name)
        """
        상품 검색 입력 필드에 제품명을 입력하고 검색 버튼을 클릭합니다.
        :param product_name: 검색할 제품명
        """
        logger.info(f"상품 검색 시도: {product_name}")
        try:
            # -> 상품 검색 입력 필드에 텍스트 입력
            self.wait_and_send_keys(self.locators.get("Product_Search_Input"), product_name, "상품 검색 입력 필드")
            self.medium_sleep()
            self.wait_and_click(self.locators.get("Search_Button"), "검색 버튼")
            logger.info(f"✅ 상품 '{product_name}' 검색 완료.")
            self.medium_sleep()
        except Exception as e:
            logger.error(f"❌ 상품 검색 실패: {e}", exc_info=True)
            self.take_screenshot("product_search_failure")
            raise

    def select_first_product(self, product_name):
        """
                검색 결과에서 첫 번째 상품을 클릭합니다.
                :param product_name: 검색했던 제품명 (로케이터 동적 생성에 사용)
                """
        logger.info(f"검색 결과에서 첫 번째 상품 '{product_name}' 선택 시도.")
        try:
            locator_template = self.locators.get("first_selection")
            dynamic_xpath = locator_template["xpath"].replace("{product_name}", product_name)
            dynamic_locator = {"xpath": dynamic_xpath}

            self.wait_and_click(dynamic_locator, f"'{product_name}' 첫 번째 상품")
            logger.info(f"✅ 첫 번째 상품 '{product_name}' 선택 완료.")
            self.medium_sleep()
        except (TimeoutException, NoSuchElementException, KeyError) as e:
            logger.error(f"❌ 첫 번째 상품 '{product_name}' 선택 실패: {e}", exc_info=True)
            self.take_screenshot("first_product_selection_failure")
            raise

    def select_sale_type_randomly(self):
        """
        '판매 구분' 옵션 중 하나를 랜덤으로 선택합니다.
        """
        logger.info("판매구분 하위 속성 중 랜덤 선택 시도.")
        self.short_sleep()
        self.select_random_option(self.locators.get("sale_type_buttons"), "'판매 구분' 버튼")

    def select_management_type_randomly(self):
        """
        '관리 유형' 옵션을 찾아서 랜덤으로 선택합니다. 노출되지 않으면 스킵합니다.
        """
        try:
            logger.info("관리 유형 하위 속성 중 랜덤 선택 시도.")
            self.swipe_up()
            self.short_sleep()
            self.select_random_option(self.locators.get("management_type_buttons"), "'관리 유형' 버튼")
        except (TimeoutException, NoSuchElementException):
            # 💡 예외를 잡아서 실패 대신 스킵으로 처리
            logger.info("ℹ️ '관리 유형'이 노출되지 않아 스킵합니다.")
            pass

    def select_mandatory_period_randomly(self):
        """
        '의무 사용 기간' 옵션을 찾아서 랜덤으로 선택합니다. 노출되지 않으면 스킵합니다.
        """
        try:
            logger.info("의무사용 기간 하위 속성 중 랜덤 선택 시도.")
            self.swipe_up()
            self.short_sleep()
            self.select_random_option(self.locators.get("mandatory_period_buttons"), "'의무 사용 기간' 버튼")
        except (TimeoutException, NoSuchElementException):
            # 💡 예외를 잡아서 실패 대신 스킵으로 처리
            logger.info("ℹ️ '의무사용 기간'이 노출되지 않아 스킵합니다.")
            pass

    def select_separate_product_randomly(self):
        """
        '별매상품' 버튼을 클릭합니다.
        """
        logger.info("'별매상품' 버튼 클릭 시도.")
        try:
            self.swipe_up()
            self.short_sleep()
            self.wait_and_click(self.locators.get("separate_product_buttons"), "별매상품 클릭")
            logger.info("✅ '별매상품' 버튼 클릭 완료.")
            self.swipe_up()
            self.short_sleep()
            self.select_random_option(self.locators.get("separate_product_details"), "'별매상품 랜덤 선택")
        except (TimeoutException, NoSuchElementException):
            logger.info("ℹ️ '별매상품'이 노출되지 않아 스킵합니다.")
            pass

    def additional_server_buttons_randomly(self):
        """
        '부가서비스' 버튼을 클릭합니다.
        """
        logger.info("'부가 서비스' 버튼 클릭 시도.")
        try:
            self.swipe_up()
            self.short_sleep()
            self.wait_and_click(self.locators.get("additional_server_buttons"), "부가서비스 클릭")
            logger.info("✅ '부가서비스' 버튼 클릭 완료.")
            self.short_sleep()
            self.select_random_option(self.locators.get("additional_server_details"), "부가서비스 랜덤 선택")
        except (TimeoutException, NoSuchElementException):
            logger.info("ℹ️ '부가서비스'가 노출되지 않아 스킵합니다.")
            pass

    def containing_goods(self):
        """
        '상품담기' 버튼을 클릭하여 상품을 장바구니에 담습니다.
        """
        logger.info("'상품담기' 버튼 클릭 시도.")
        try:
            self.wait_and_click(self.locators.get("containing_goods"), "상품담기 버튼")
            logger.info("✅ '상품담기' 버튼 클릭 완료.")
            self.medium_sleep()
        except Exception as e:
            logger.error(f"❌ '상품담기' 버튼 클릭 실패: {e}", exc_info=True)
            self.take_screenshot("add_product_to_cart_failure")
            raise

    def adding_goods(self):
        """
        '상품 추가하기' 버튼을 클릭하여 상품을 추가로 주문합니다.
        """
        logger.info("'상품 추가하기' 버튼 클릭 시도.")
        try:
            self.wait_and_click(self.locators.get("adding_goods"), "상품추가 하기 버튼")
            logger.info("✅ '상품 추가하기' 버튼 클릭 완료.")
            self.long_sleep()
        except Exception as e:
            logger.error(f"❌ '상품 추가하기' 버튼 클릭 실패: {e}", exc_info=True)
            self.take_screenshot("add_product_to_cart_failure")
            raise

    def enter_discount_information(self):
        """
        '할인정보 입력하기' 버튼을 클릭하여 Step3로 이동.
        """
        logger.info("'할인 정보 입력' 버튼 클릭 시도.")
        try:
            self.wait_and_click(self.locators.get("enter_discount_information"), "할인 정보 입력 버튼")
            logger.info("✅ '할인 정보 입력' 버튼 클릭 완료.")
            self.long_sleep()
        except Exception as e:
            logger.error(f"❌ '할인 정보 입력' 버튼 클릭 실패: {e}", exc_info=True)
            self.take_screenshot("add_product_to_cart_failure")
            raise