# -*- coding: utf-8 -*-
# JSON 파일 처리를 위한 모듈을 가져옵니다.
import json
# 파일 시스템 경로 처리를 위한 모듈을 가져옵니다.
import os
# 로그 기록을 위한 커스텀 로거 인스턴스를 가져옵니다.
from utils.logger import logger


class ConfigManager:
    """
    JSON 설정 파일(config.json)과 테스트 데이터(test_data.json)를
    로드하고 관리하는 클래스입니다.
    이 클래스는 프로젝트의 어떤 위치에서든 파일에 안정적으로 접근할 수 있도록 경로를 관리합니다.
    """

    def __init__(self):
        # 현재 파일의 절대 경로를 기준으로 프로젝트의 루트 경로를 정의합니다.
        # 이렇게 하면 pytest가 테스트를 실행하는 방식에 상관없이 항상 올바른 경로를 찾을 수 있습니다.
        # 'utils' 폴더의 부모 폴더, 즉 프로젝트의 루트 폴더를 찾습니다.
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

        # 프로젝트 루트 경로에 'config.json' 파일 이름을 결합하여 전체 경로를 생성합니다.
        config_file_path = os.path.join(self.project_root, 'config.json')

        # 설정 파일을 로드합니다.
        self.config = self._load_json(config_file_path, "설정")

    def _load_json(self, file_path, file_type):
        """
        주어진 경로의 JSON 파일을 읽어와 딕셔너리 형태로 반환합니다.
        파일이 존재하지 않거나 형식이 잘못된 경우 오류를 로깅하고 예외를 발생시킵니다.
        """
        if not os.path.exists(file_path):
            logger.error(f"{file_type} 파일이 존재하지 않습니다: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 파일의 모든 내용을 읽어와 JSON 형태로 변환하고 반환합니다.
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"{file_type} 파일 디코딩 오류: {file_path}. JSON 형식을 확인하세요. {e}")
            raise
        except Exception as e:
            logger.error(f"{file_type} 파일 로딩 중 예기치 않은 오류 발생: {e}")
            raise

    def get_test_data(self):
        """
        'data/test_data.json' 파일의 테스트 데이터를 로드하여 반환합니다.
        """
        # 프로젝트 루트 경로에 'data' 폴더와 'test_data.json' 파일 이름을 결합하여 경로를 생성합니다.
        data_file_path = os.path.join(self.project_root, 'data', 'test_data.json')
        return self._load_json(data_file_path, "테스트 데이터")
