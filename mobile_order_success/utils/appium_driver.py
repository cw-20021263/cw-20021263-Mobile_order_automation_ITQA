# -*- coding: utf-8 -*-
# --- 필수 모듈 임포트 ---
import pytest
import subprocess
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from utils.config_manager import ConfigManager
from utils.logger import logger
import os


# --- 헬퍼 함수: 설정 유효성 검사 ---
def get_platform_from_config(device_config):
    """
    config.json에서 platformName 값을 가져와 유효성을 검사합니다.
    :param device_config: config.json에서 가져온 디바이스 설정 딕셔너리
    :return: 유효한 플랫폼 이름 (소문자)
    """
    platform = device_config.get("platformName")
    if not platform or platform.lower() not in ['android', 'ios']:
        error_message = "❌ 'config.json' 파일에 'platformName' 키가 누락되었거나 값이 유효하지 않습니다. (허용 값: 'Android', 'iOS')"
        logger.error(error_message)
        pytest.fail(error_message)
    return platform.lower()


# --- 메인 드라이버 초기화 함수 ---
# CHANGED: platform_name 인자를 추가하여 플랫폼을 명시적으로 지정합니다.
def init_appium_driver(platform_name=None):
    """
    Appium WebDriver 인스턴스를 초기화하고 반환합니다.
    :return: 초기화된 Appium WebDriver 인스턴스 및 플랫폼 이름
    """
    config_manager = ConfigManager()
    appium_server_url = config_manager.config.get("Appium", {}).get("server_url", "http://127.0.0.1:4723/wd/hub")

    # CHANGED: 플랫폼 이름이 명시적으로 주어지지 않으면, config.json의 기본 Android 설정을 사용합니다.
    if not platform_name:
        platform_name = "Android"

    device_config_key = f"Capabilities_{platform_name}"
    device_config = config_manager.config.get(device_config_key, {})

    if 'platformName' not in device_config:
        device_config['platformName'] = platform_name

    if platform_name.lower() == 'android':
        options = UiAutomator2Options().load_capabilities(device_config)
    elif platform_name.lower() == 'ios':
        options = XCUITestOptions().load_capabilities(device_config)
    else:
        # 이 예외는 위 로직으로 인해 거의 발생하지 않습니다.
        raise ValueError("유효하지 않은 플랫폼입니다. 'Android' 또는 'iOS'여야 합니다.")

    try:
        driver = webdriver.Remote(appium_server_url, options=options)
        logger.info(f"✅ Appium 드라이버가 성공적으로 초기화되었습니다. (플랫폼: {platform_name})")
        return driver, platform_name
    except Exception as e:
        error_message = f"❌ Appium 드라이버 초기화 실패: {e}"
        logger.error(error_message)
        pytest.fail(error_message)