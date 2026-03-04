# -*- coding: utf-8 -*-
import pytest
from utils.appium_driver import init_appium_driver


# 1. 커스텀 명령줄 인자(--platform) 등록
def pytest_addoption(parser):
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        help="실행 플랫폼 설정 (android 또는 ios)"
    )


# 2. 플랫폼 정보 fixture
@pytest.fixture(scope="session")
def platform(request):
    return request.config.getoption("--platform").lower()


# 3. 드라이버 초기화 및 종료 fixture
@pytest.fixture(scope="function")
def driver(platform):
    # utils/appium_driver.py의 함수를 호출하여 드라이버 생성
    driver_instance, platform_name = init_appium_driver(platform)

    yield driver_instance

    # 테스트 종료 후 드라이버 종료
    if driver_instance:
        driver_instance.quit()