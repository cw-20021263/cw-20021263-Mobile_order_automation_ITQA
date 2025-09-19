# pages/digitalsales_login.pyas

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.base_page import BasePage
from utils.config_manager import ConfigManager
# -> 싱글턴 locator_manager 인스턴스를 직접 임포트합니다.
from utils.locator_manager import locator_manager
from utils.logger import logger

class DigitalSalesLoginPage(BasePage):
    def __init__(self, driver, platform):
        super().__init__(driver, platform)
        # -> 플랫폼을 설정하고 필요한 로케이터를 가져옵니다.
        locator_manager.set_platform(platform)
        self.locators = locator_manager.get_locators("digitalsales_locators")
        self.test_data = ConfigManager().get_test_data()

    def login(self, username=None, password=None):
        """
        사용자 이름과 비밀번호를 입력하여 앱에 로그인하는 함수입니다.
        """
        username_to_use = username if username else self.test_data["UserData"]["VALID_INDIVIDUAL_ID"]
        password_to_use = password if password else self.test_data["UserData"]["VALID_INDIVIDUAL_PASSWORD"]

        logger.info(f"디지털세일즈 앱 로그인 시도: 사용자명={username_to_use}")
        try:
            # -> 앱 초기 접속 시 나타나는 팝업의 '확인' 버튼을 클릭합니다.
            try:
                # -> 타임아웃을 5초로 설정하여 불필요한 대기 시간을 줄입니다.
                self.wait_and_click(self.locators.get("access_button"), "접속 확인 버튼", timeout=2)
                logger.info("초기 접속 확인 버튼 클릭 완료.")
            except (TimeoutException, NoSuchElementException, ValueError):
                # -> 버튼이 없거나 로케이터가 유효하지 않으면 로그만 남기고 넘어갑니다.
                logger.info("초기 접속 확인 버튼이 나타나지 않거나 로케이터가 유효하지 않아 스킵합니다.")

            # -> ID, 비밀번호 입력 및 로그인 버튼 클릭
            self.wait_and_send_keys(self.locators.get("id_input"), username_to_use, "로그인 ID 필드")
            self.wait_and_send_keys(self.locators.get("password_input"), password_to_use, "로그인 비밀번호 필드")
            self.short_sleep()
            self.wait_and_click(self.locators.get("login_button"), "로그인 버튼")
            logger.info("로그인 버튼 클릭 완료.")
            self.medium_sleep()

            # -> 위치 권한 허용 팝업 처리
            try:
                self.wait_and_click(self.locators.get("location_permission_button"), "위치 권한 허용 버튼", timeout=5)
                logger.info("위치 권한 허용 버튼 클릭 완료.")
            except (TimeoutException, NoSuchElementException, ValueError):
                logger.info("위치 권한 허용 팝업이 나타나지 않아 스킵합니다.")

            logger.info("디지털세일즈 앱 로그인 성공.")
        except Exception as e:
            # -> 실패 시 로그를 남기고 스크린샷을 찍은 후 예외를 다시 발생시켜 테스트를 중단합니다.
            logger.error(f"디지털세일즈 앱 로그인 실패: {e}", exc_info=True)
            self.take_screenshot("login_failure")
            raise
