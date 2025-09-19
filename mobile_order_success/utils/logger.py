# 필요한 모듈들을 가져옵니다.
import logging # 파이썬에서 로그를 기록하는 표준 모듈
import os # 파일 경로를 다루는 모듈 (예: 폴더 만들기)
from datetime import datetime # 현재 시간을 가져오는 모듈
import threading # 여러 작업을 동시에 진행할 때 충돌을 막아주는 모듈

class Logger:
    """
    테스트 진행 상황을 기록하는 클래스입니다.
    이 클래스는 프로그램 전체에서 하나의 로거 인스턴스만 사용하도록 보장합니다.
    """
    # 클래스 변수: 로거 인스턴스를 저장할 변수 (초기값은 None)
    _logger_instance = None
    # 클래스 변수: 스레드 간 충돌을 막기 위한 잠금(lock) 객체
    _logger_lock = threading.Lock()

    @classmethod
    def get_logger(cls):
        """
        로그를 기록하기 위한 설정을 하고, 로거 객체를 반환하는 함수입니다.
        클래스 메서드이므로 'cls'를 첫 번째 인자로 받습니다.
        """
        # 스레드 잠금을 사용하여, 한 번에 한 스레드만 이 코드 블록을 실행하도록 합니다.
        with cls._logger_lock:
            # 만약 로거 인스턴스가 아직 만들어지지 않았다면 (첫 호출일 때),
            if cls._logger_instance is None:
                # 현재 파일의 위치를 기준으로 프로젝트의 가장 위쪽(루트) 폴더를 찾습니다.
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                # 로그 파일을 저장할 'reports/logs' 폴더의 경로를 만듭니다.
                log_dir = os.path.join(project_root, 'reports', 'logs')
                # 해당 폴더가 없으면 새로 만듭니다. (있으면 그냥 넘어갑니다)
                os.makedirs(log_dir, exist_ok=True)

                # 현재 날짜와 시간을 기반으로 로그 파일 이름을 만듭니다.
                log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
                # 로그 파일의 전체 경로를 만듭니다.
                log_filepath = os.path.join(log_dir, log_filename)

                # 'MobileOrderTestLogger'라는 이름의 로거 객체를 만듭니다.
                logger = logging.getLogger("MobileOrderTestLogger")
                # 로거의 레벨을 'INFO'로 설정하여, INFO 이상의 중요한 메시지만 기록하도록 합니다.
                logger.setLevel(logging.INFO)

                # 만약 로거에 아직 핸들러(로그를 처리하는 방법)가 등록되지 않았다면,
                if not logger.handlers:
                    # --- 로그를 화면에 보여주는(콘솔) 핸들러 설정 ---
                    # 화면에 로그를 출력하는 객체를 만듭니다.
                    console_handler = logging.StreamHandler()
                    # 로그 메시지의 형식을 지정합니다. (시간 - 레벨 - 메시지)
                    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                    # 포맷을 핸들러에 적용합니다.
                    console_handler.setFormatter(console_formatter)
                    # 핸들러를 로거에 추가합니다.
                    logger.addHandler(console_handler)

                    # --- 로그를 파일에 저장하는 핸들러 설정 ---
                    # 파일에 로그를 쓰는 객체를 만듭니다. (경로, 인코딩 지정)
                    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
                    # 로그 메시지의 형식을 지정합니다.
                    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                    # 포맷을 핸들러에 적용합니다.
                    file_handler.setFormatter(file_formatter)
                    # 핸들러를 로거에 추가합니다.
                    logger.addHandler(file_handler)

                # 최종적으로 완성된 로거 인스턴스를 클래스 변수에 저장합니다.
                cls._logger_instance = logger

        # 로거 인스턴스를 반환하여 다른 곳에서 사용할 수 있게 합니다.
        return cls._logger_instance

# 다른 파일에서 이 모듈을 임포트하면, 아래 코드가 바로 실행됩니다.
# 싱글톤 패턴에 따라, 이 시점에 로거 인스턴스가 처음으로 만들어집니다.
logger = Logger.get_logger()
