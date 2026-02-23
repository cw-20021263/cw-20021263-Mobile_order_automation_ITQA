# -*- coding: utf-8 -*-
from pages.base_page import BasePage
from utils.locator_manager import locator_manager
from utils.logger import logger


class OrderStatusPage(BasePage):
    """
    모바일 주문의 '주문 현황' 페이지를 나타내는 클래스입니다.
    이 클래스는 특정 고객의 주문 상태를 확인하고 상호작용하는 동작을 정의합니다.
    """

    def __init__(self, driver, platform):
        super().__init__(driver, platform)
        locator_manager.set_platform(platform)
        self.locators = locator_manager.get_locators("Order_Status")

    def verify_auth_button_for_customer(self, customer_name):
        """
        -> [변경] 주문 현황 목록에서 특정 고객 이름과 '인증입력' 버튼이 함께 노출되는지 확인합니다. (클릭 X)
        """
        logger.info(f"주문 현황 페이지에서 고객 '{customer_name}'의 '인증입력' 버튼 노출 여부를 확인합니다.")
        try:
            # 고객 이름에 해당하는 로케이터를 동적으로 생성합니다.
            customer_name_locator = self.locators.get("Customer_Name").copy()
            if customer_name_locator and 'xpath' in customer_name_locator:
                customer_name_locator['xpath'] = customer_name_locator['xpath'].replace('{customer_name}',
                                                                                        customer_name)
            else:
                raise ValueError("Customer_Name 로케이터에 'xpath'가 없습니다.")

            # 해당 고객 이름이 화면에 표시될 때까지 기다립니다.
            customer_element = self.find_element_with_fallback(customer_name_locator)
            if not customer_element:
                raise Exception(f"고객 '{customer_name}'을(를) 주문 현황 목록에서 찾을 수 없습니다.")

            # -> [추가] 화면에 표시된 실제 고객 이름과 예상 고객 이름을 비교하는 로그를 추가합니다.
            actual_name = customer_element.text.strip()
            logger.info(f"👉 고객 이름 비교: [예상] '{customer_name}' vs [실제] '{actual_name}'")

            logger.info(f"고객 '{customer_name}'이(가) 주문 현황 목록에서 확인되었습니다.")

            # -> [변경] '인증입력' 버튼이 보이는지 확인만 하고 클릭은 하지 않습니다.
            auth_button = self.find_element_with_fallback(self.locators.get("Enter_Authentication_Button"))
            if auth_button:
                logger.info(f"고객 '{customer_name}'의 '인증입력' 버튼이 정상적으로 노출됩니다.")
            else:
                raise Exception(f"고객 '{customer_name}'의 '인증입력' 버튼을 찾을 수 없습니다.")

            self.short_sleep()

        except Exception as e:
            logger.error(f"고객 '{customer_name}'의 주문 혹은 '인증입력' 버튼 확인에 실패했습니다: {e}", exc_info=True)
            self.take_screenshot("verify_auth_button_failure")
            raise

    def focus_customer_search_and_type(self, text: str):
        """
        주문현황 상단 고객 검색 입력창에 포커스를 주고 텍스트를 입력합니다.
        - WebView/Hybrid 화면에서는 '보임'만으로는 입력이 안 되는 경우가 있어 클릭(포커스) 후 입력합니다.
        """
        search_locator = self.locators.get("customer_search")
        self.wait_and_click(search_locator, "고객 검색 입력창(포커스)")
        self.wait_and_send_keys(search_locator, text, "고객 검색 입력창")
        self.short_sleep()