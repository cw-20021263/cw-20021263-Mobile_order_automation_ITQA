# pages/order_status_completed.py

from selenium.common.exceptions import TimeoutException, NoSuchElementException

# -*- coding: utf-8 -*-
from pages.base_page import BasePage
from utils.logger import logger
from utils.locator_manager import locator_manager

class OrderStatusCompletedPage(BasePage):
    """
    주문 현황에서 '인증완료' 단계의 주문을 관리하는 페이지 객체입니다.
    이 클래스는 '인증완료' 버튼을 클릭하고 고객 정보를 확인하는 기능을 제공합니다.
    """
    # -> [변경] __init__ 함수에서 self.locators를 초기화하여,
    #    다른 메서드들이 로케이터를 사용할 수 있도록 합니다.
    def __init__(self, driver, platform):
        super().__init__(driver, platform)
        locator_manager.set_platform(platform)
        self.locators = locator_manager.get_locators("Order_Status")

    def click_auth_completed_for_customer(self, customer_name):
        """
        주문 현황 목록에서 '인증완료'와 일치하는 고객의 '인증완료' 버튼을 클릭합니다.
        :param customer_name: 인증 완료 여부를 확인할 고객 이름
        """
        logger.info(f"주문 현황에서 고객 '{customer_name}'의 '인증완료' 버튼 클릭 시도.")
        try:
            auth_button_text = "인증완료"

            # '인증완료' 버튼과 고객명 TextView가 동일한 부모 View 아래에 있는
            # 형제 관계인 점을 고려하여 XPath를 수정했습니다.
            dynamic_xpath = f"//android.widget.Button[@text='{auth_button_text}' and following-sibling::android.view.View[./android.widget.TextView[@text='{customer_name}']]]"

            dynamic_locator = {'xpath': dynamic_xpath}

            self.wait_and_click(
                locator=dynamic_locator,
                element_name=f"'{customer_name}' 고객의 '인증완료' 버튼"
            )

            logger.info(f"✅ 고객 '{customer_name}'의 '인증완료' 버튼 클릭 완료.")

        except (TimeoutException, NoSuchElementException, ValueError) as e:
            logger.error(f"❌ 고객 '{customer_name}'의 '인증완료' 버튼을 찾거나 클릭하지 못했습니다.", exc_info=True)
            self.take_screenshot("click_auth_completed_failure")
            raise

    def click_order_continue(self):
        """
        '주문 이어서 하기' 버튼을 클릭합니다.
        """
        logger.info("주문 이어서 하기 버튼 클릭 시도.")
        try:
            self.wait_and_click(
                locator=self.locators.get("order_continue"),
                element_name="'주문 이어서 하기' 버튼"
            )
            self.medium_sleep()
            logger.info("✅ '주문 이어서 하기' 버튼 클릭 완료.")
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"❌ '주문 이어서 하기' 버튼을 찾거나 클릭하지 못했습니다.", exc_info=True)
            self.take_screenshot("click_order_continue_failure")
            raise