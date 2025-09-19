# pages/auth_page.py
from pages.base_page import BasePage
from utils.config_manager import ConfigManager
# -> 싱글턴 locator_manager 인스턴스를 직접 임포트합니다.
from utils.locator_manager import locator_manager
from utils.logger import logger

class AuthPage(BasePage):
    """
    모바일 주문 서비스의 고객 인증 페이지를 나타내는 클래스입니다.
    이 클래스는 '개인'/'개인사업자' 선택, 고객명/휴대폰 번호 입력 등 인증 관련 동작을 정의합니다.
    """
    def __init__(self, driver, platform):
        super().__init__(driver, platform)
        # -> 수정된 locator_manager 사용 방식에 맞춰 코드를 수정합니다.
        locator_manager.set_platform(platform)
        self.locators = locator_manager.get_locators("auth_page_locators")
        self.test_data = ConfigManager().get_test_data()

    def select_individual_customer_type(self):
        """
        '개인' 버튼을 클릭하여 개인 고객 유형을 선택하는 함수입니다.
        """
        logger.info("'개인' 고객 유형 선택 시도.")
        try:
            # -> self.locators를 사용하도록 수정합니다.
            self.wait_and_click(self.locators.get("individual_button"), "'개인' 버튼")
            logger.info("'개인' 고객 유형 선택 완료.")
            self.medium_sleep()
        except Exception as e:
            logger.error(f"'개인' 고객 유형 선택 실패: {e}", exc_info=True)
            self.take_screenshot("select_individual_customer_type_failure")
            raise

    def select_business_customer_type(self):
        """
        '개인사업자' 버튼을 클릭하여 개인사업자 고객 유형을 선택하는 함수입니다.
        """
        logger.info("'개인사업자' 고객 유형 선택 시도.")
        try:
            # -> self.locators를 사용하도록 수정합니다.
            self.wait_and_click(self.locators.get("business_button"), "'개인사업자' 버튼")
            logger.info("'개인사업자' 고객 유형 선택 완료.")
            self.medium_sleep()
        except Exception as e:
            logger.error(f"'개인사업자' 고객 유형 선택 실패: {e}", exc_info=True)
            self.take_screenshot("select_business_customer_type_failure")
            raise

    def enter_customer_name(self, name=None):
        """
        고객명 입력 필드에 이름을 입력하는 함수입니다.
        """
        name_to_use = name if name else self.test_data["CustomerData"]["VALID_CUSTORMER_NAME"]
        logger.info(f"고객명 입력 시도: {name_to_use}")
        try:
            # -> self.locators를 사용하도록 수정합니다.
            self.wait_and_send_keys(self.locators.get("name_input"), name_to_use, "고객명 입력 필드")
            logger.info(f"고객명 '{name_to_use}' 입력 완료.")
            self.short_sleep()
        except Exception as e:
            logger.error(f"고객명 입력 실패: {e}", exc_info=True)
            self.take_screenshot("enter_customer_name_failure")
            raise

    def enter_phone_number(self, phone_number=None):
        """
        휴대폰 번호 입력 필드에 번호를 입력하는 함수입니다.
        """
        phone_to_use = phone_number if phone_number else self.test_data["CustomerData"]["VALID_CUSTORMER_PHONE"]
        logger.info(f"휴대폰 번호 입력 시도: {phone_to_use}")
        try:
            # -> self.locators를 사용하도록 수정합니다.
            self.wait_and_send_keys(self.locators.get("phone_number_input"), phone_to_use, "휴대폰 번호 입력 필드")
            logger.info(f"휴대폰 번호 '{phone_to_use}' 입력 완료.")
            self.short_sleep()
            self.hide_keyboard()
        except Exception as e:
            logger.error(f"휴대폰 번호 입력 실패: {e}", exc_info=True)
            self.take_screenshot("enter_phone_number_failure")
            raise

    def click_auth_request_button(self):
        """
        '본인인증 요청' 버튼을 클릭하는 함수입니다.
        """
        logger.info("'본인인증 요청' 버튼 클릭 시도.")
        try:
            # -> self.locators를 사용하도록 수정합니다.
            self.wait_and_click(self.locators.get("auth_request_button"), "'본인인증 요청' 버튼")
            logger.info("'본인인증 요청' 버튼 클릭 완료.")
            self.medium_sleep()
        except Exception as e:
            logger.error(f"'본인인증 요청' 버튼 클릭 실패: {e}", exc_info=True)
            self.take_screenshot("click_auth_request_button_failure")
            raise

    def confirm_message_send_popup(self):
        """
        고객인증 메시지 발송 확인 팝업에서 '발송' 버튼을 클릭하는 함수입니다.
        """
        logger.info("고객인증 메시지 발송 확인 팝업에서 '발송' 버튼 클릭 시도.")
        try:
            # -> self.locators를 사용하도록 수정합니다.
            self.wait_and_click(self.locators.get("message_send_button"), "'발송' 버튼 (메시지 발송 팝업)")
            logger.info("고객인증 메시지 발송 확인 팝업에서 '발송' 버튼 클릭 완료.")
            self.long_sleep()
        except Exception as e:
            logger.error(f"메시지 발송 확인 팝업 처리 실패: {e}", exc_info=True)
            self.take_screenshot("confirm_message_send_popup_failure")
            raise

    def cancel_message_send_popup(self):
        """
        고객인증 메시지 발송 확인 팝업에서 '취소' 버튼을 클릭하는 함수입니다.
        """
        logger.info("고객인증 메시지 발송 확인 팝업에서 '취소' 버튼 클릭 시도.")
        try:
            # -> self.locators를 사용하도록 수정합니다.
            self.wait_and_click(self.locators.get("message_cancel_button"), "'취소' 버튼 (메시지 발송 팝업)")
            logger.info("고객인증 메시지 발송 확인 팝업에서 '취소' 버튼 클릭 완료.")
            self.medium_sleep()
        except Exception as e:
            logger.error(f"메시지 발송 취소 팝업 처리 실패: {e}", exc_info=True)
            self.take_screenshot("cancel_message_send_popup_failure")
            raise

    def perform_customer_authentication(self, customer_type=None, name=None, phone_number=None, confirm_send=True):
        """
        고객 인증의 전체 과정을 처음부터 끝까지 수행하는 함수입니다.
        """
        customer_type_to_use = customer_type or self.test_data["CustomerData"]["VALID_CUSTORMER_TYPE"]
        name_to_use = name or self.test_data["CustomerData"]["VALID_CUSTORMER_NAME"]
        phone_to_use = phone_number or self.test_data["CustomerData"]["VALID_CUSTORMER_PHONE"]

        logger.info(f"고객 인증 전체 흐름 시작: 유형={customer_type_to_use}, 이름={name_to_use}, 휴대폰={phone_to_use}")
        try:
            if customer_type_to_use == "개인":
                self.select_individual_customer_type()
            elif customer_type_to_use == "개인사업자":
                self.select_business_customer_type()
            else:
                raise ValueError("유효하지 않은 고객 유형입니다. '개인' 또는 '개인사업자'를 입력해주세요.")

            self.enter_customer_name(name_to_use)
            self.enter_phone_number(phone_to_use)
            self.click_auth_request_button()

            if confirm_send:
                self.confirm_message_send_popup()
            else:
                self.cancel_message_send_popup()

            logger.info("고객 인증 전체 흐름 완료.")
        except Exception as e:
            logger.error(f"고객 인증 전체 흐름 실패: {e}", exc_info=True)
            self.take_screenshot("perform_customer_authentication_failure")
            raise
