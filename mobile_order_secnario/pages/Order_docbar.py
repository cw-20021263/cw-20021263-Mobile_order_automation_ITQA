# pages/Order_docbar.py
from pages.base_page import BasePage
# -> 싱글턴 locator_manager 인스턴스를 직접 임포트합니다.
from utils.locator_manager import locator_manager
from utils.logger import logger


class MobileOrderPage(BasePage):
    """
    디지털세일즈 앱의 독바를 통해 모바일 주문에 접속하고
    일반 주문을 시작하는 페이지 객체입니다.
    """
    def __init__(self, driver, platform):
        super().__init__(driver, platform)
        # -> 수정된 locator_manager 사용 방식에 맞춰 코드를 수정합니다.
        locator_manager.set_platform(platform)
        # -> 올바른 페이지 키('test_order')로 로케이터를 가져옵니다.
        self.locators = locator_manager.get_locators("test_order")

    def access_mobile_order_via_docbar(self):
        """
        디지털세일즈 앱 독바의 '모바일 주문' 버튼을 클릭하여 모바일 주문 서비스에 접속합니다.
        """
        logger.info("독바를 통해 '모바일 주문' 접속 시도.")
        try:
            # -> self.locators를 사용하도록 수정합니다.
            self.wait_and_click(self.locators.get("mobile_order_button"), "'모바일 주문' 버튼")
            logger.info("독바 '모바일 주문' 버튼 클릭 완료.")
            self.medium_sleep()
            logger.info("모바일 주문 서비스 진입 확인.")
        except Exception as e:
            logger.error(f"독바를 통한 '모바일 주문' 접속 실패: {e}", exc_info=True)
            self.take_screenshot("access_mobile_order_docbar_failure")
            raise

    def start_general_order(self):
        """
        모바일 주문 서비스에서 '일반 주문하기' 버튼을 클릭하여 주문을 시작합니다.
        """
        logger.info("'일반 주문하기' 시작 시도.")
        try:
            # -> self.locators를 사용하도록 수정합니다.
            self.wait_and_click(self.locators.get("general_order_button"), "'일반 주문하기' 버튼")
            logger.info("'일반 주문하기' 버튼 클릭 완료.")
            self.medium_sleep()
            logger.info("'일반 주문하기' 시작 및 다음 단계 진입 확인.")
        except Exception as e:
            logger.error(f"'일반 주문하기' 시작 실패: {e}", exc_info=True)
            self.take_screenshot("start_general_order_failure")
            raise
