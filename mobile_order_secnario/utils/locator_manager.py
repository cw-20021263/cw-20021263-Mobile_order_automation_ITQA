# -*- coding: utf-8 -*-
import json
import os
import threading
from utils.logger import logger
from utils.config_manager import ConfigManager


class LocatorManager:
    """
    [싱글턴 패턴 적용] 모든 로케이터 JSON 파일을 한 번만 로드하여 메모리에 저장하고 관리합니다.
    이를 통해 파일 접근을 최소화하고 성능을 향상시킵니다.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self.config_manager = ConfigManager()
                    self.FILE_KEY_MAP = {
                        "Digitalsales_locators": "digitalsales_locators",
                        "Order_Docbar_locators": "test_order",
                        "Auth_page_locators": "auth_page_locators",
                        "Order_Status_locators": "Order_Status",
                        "product_select_locators": "product_select",
                    }
                    self._all_locators = self._load_all_locators()
                    self.platform = None
                    self._initialized = True

    def _load_json(self, file_path):
        if not os.path.exists(file_path):
            logger.error(f"로케이터 파일이 존재하지 않습니다: {file_path}")
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"JSON 디코딩 오류: {file_path}. 파일 형식을 확인하세요.")
            return None

    def _load_all_locators(self):
        all_locators = {}
        locators_path = os.path.join(self.config_manager.project_root, 'locators')
        if not os.path.exists(locators_path):
            logger.error(f"로케이터 디렉토리가 존재하지 않습니다: {locators_path}")
            return {}

        for file_name_with_ext in os.listdir(locators_path):
            if file_name_with_ext.endswith(".json"):
                file_name_from_disk = file_name_with_ext.replace(".json", "")

                # -> [오류 수정] 파일 시스템과 코드 간의 파일명 대소문자 불일치 문제를 해결하기 위해,
                # -> 파일명을 소문자로 변환하여 비교하는 로직을 추가합니다.
                group_key = None
                found_map_key = None
                for map_key in self.FILE_KEY_MAP.keys():
                    if map_key.lower() == file_name_from_disk.lower():
                        found_map_key = map_key
                        break

                if found_map_key:
                    group_key = self.FILE_KEY_MAP[found_map_key]
                    file_path = os.path.join(locators_path, file_name_with_ext)
                    data = self._load_json(file_path)
                    if data:
                        if group_key in data:
                            all_locators[group_key] = data[group_key]
                        else:
                            logger.info(f"'{file_name_with_ext}' 파일에 최상위 키 '{group_key}'가 없어, 파일 전체를 로케이터 그룹으로 로드합니다.")
                            all_locators[group_key] = data
                    else:
                        logger.warning(f"'{file_name_with_ext}' 파일이 비어있거나 유효하지 않아 로드하지 못했습니다.")

        logger.info(f"모든 로케이터 로딩 완료. 로드된 그룹: {list(all_locators.keys())}")
        return all_locators

    def set_platform(self, platform):
        if platform:
            self.platform = platform.lower()

    def get_locators(self, page_key):
        """
        페이지 키(예: 'digitalsales_locators')에 해당하는 로케이터들을 현재 플랫폼에 맞게 반환합니다.
        """
        if not self.platform:
            raise Exception("플랫폼이 설정되지 않았습니다. set_platform()을 먼저 호출하세요.")

        locators_in_group = self._all_locators.get(page_key, {})
        if not locators_in_group:
            logger.error(f"'{page_key}'에 해당하는 로케이터 그룹을 찾을 수 없습니다.")
            return {}

        platform_locators = {}
        for key, value in locators_in_group.items():
            if isinstance(value, dict) and self.platform in value:
                platform_locators[key] = value[self.platform]
            else:
                logger.warning(f"'{key}' 로케이터에 '{self.platform}' 플랫폼 정보가 없거나 형식이 잘못되었습니다.")
                platform_locators[key] = None
        return platform_locators


locator_manager = LocatorManager()

