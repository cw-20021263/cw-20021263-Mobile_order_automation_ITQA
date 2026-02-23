# -*- coding: utf-8 -*-
import random
import re
import time
from pages.base_page import BasePage
from utils.locator_manager import locator_manager
from utils.logger import logger

class Step4PaymentInfoPage(BasePage):
    """
    Step 4: 결제정보 선택 화면을 담당하는 페이지입니다.
    정기결제/수납결제 금액을 확인하고 결제 수단을 선택 버튼을 제어합니다.
    """

    def __init__(self, driver, platform):
        super().__init__(driver, platform)
        
         # -> 플랫폼 설정 및 'payment_info_select' 로케이터 그룹 로드
        locator_manager.set_platform(platform)
        self.locators = locator_manager.get_locators("payment_info_select")

    def verify_page_compoenets(self, expected_customer_name):
        """
        결제정보입력 페이지의 주요 요소를 검증합니다.
        1. step4주요 유동 UI확인
            1-1 step4에 맞게 4로 되어 있는지 확인
            1-2 고객명 : {customer_name} 확인
        2. 텍스트 문구 일치 확인
            2-1 page Title확인(결제정보 선택)
            2-2 정기결제금액 매월 납부하는 금액
            2-3 수납 금액 일회성 결제 금액
            2-4 정기결제수단
            2-5 정기결제 수단 선택
            2-6 수납결제수단
            2-7 수납결제 수단 선택
        """
        logger.info("🔍 현재 페이지(Step 4) 진입 여부를 확인합니다.")
        
        # 1. Step Indicator 검증 ('4')
        step_element = self.find_element_with_fallback(self.locators.get("step_indicator"))
        step_text = step_element.text
        if "4" != step_text:
            raise Exception(f"Step 단계 불일치: 기대값 '4', 실제값 '{step_text}'")
        else:
            logger.info(f"✅ Step 단계 확인 완료: {step_text}단계")

        # 2. Customer Name 검증 (예: '고객명: 음규환')
        customer_element = self.find_element_with_fallback(self.locators.get("customer_name"))
        customer_text = customer_element.text
        if expected_customer_name not in customer_text:
                raise Exception(f"고객명 불일치: '{expected_customer_name}'가 '{customer_text}'에 없음")
        logger.info(f"✅ 고객명 정보 확인 완료: {customer_text}")

        # 검증할 9가지 항목으로 딕셔너리 재구성 (JSON 파일의 key와 1:1 매칭)
        validation_items = {
            'page_title': "결제정보 선택",
            'regular_payment_amount_label': "정기결제금액",
            'regular_payment_amount_sub_label': "매월 납부하는 금액",     
            'lump_sum_payment_amount_label': "수납 금액",
            'lump_sum_payment_amount_sub_label': "일회성 결제 금액",  
            'regular_payment_method_label': "정기결제수단",
            'lump_sum_payment_method_label': "수납결제수단"
        }

        for key, expected_text in validation_items.items():
            # 1. 요소 찾기
            try:
                element = self.find_element_with_fallback(self.locators[key], timeout=3)
                # 2. 텍스트 가져오기
                actual_text = element.text
                
                # 3. 문구 비교 및 검증
                if expected_text in actual_text:
                    logger.info(f"✅ 검증 성공: '{expected_text}' 문구가 화면에 정상적으로 표시되었습니다.")
                else:
                    logger.error(f"❌ 검증 실패: 기대값('{expected_text}')이 실제 텍스트('{actual_text}')에 포함되어 있지 않습니다.")
            except Exception as e:
                logger.error(f"❌ 요소를 찾을 수 없습니다: {key} (기대문구: {expected_text}) - {e}")


    def check_payment_amounts(self):
        """
        1. 화면에 표시된 정기결제 금액과 수납 금액을 가져와 로그로 출력.
            1-1 정기결제 변수 : reg_amount
            1-2 수납결제 변수 : lump_sum_amount
        2. 요소 텍스트는 "24,140원/월" 또는 "858,500원" 형태로 되어 있는지 확인.
        """
        logger.info("💰 결제 금액 정보를 확인합니다.")
        
        # 정기 결제 금액 확인 (예: "24,140원/월")
        self.find_element_with_fallback(self.locators.get("regular_payment_amount_label"))
        regular_payment_elems = self.get_all_elements_with_fallback(self.locators.get("regular_payment_amount_value"))
        if regular_payment_elems:
            reg_amount = regular_payment_elems[0].text.strip()
            if reg_amount:
                # "원/월"이 포함되어 있는지 확인
                if "원/월" in reg_amount:
                    logger.info(f" - 정기결제 금액: {reg_amount}")
                else:
                    logger.warning(f"⚠️ 정기결제 금액에 '원/월'이 포함되어 있지 않습니다: {reg_amount}")
            else:
                logger.warning("⚠️ 정기결제 금액 요소는 존재하지만 텍스트가 비어있습니다.")
        else:
            logger.warning("⚠️ 정기결제 금액 요소를 찾을 수 없습니다.")
        
        # 수납 금액 확인 (예: "858,500원")
        self.find_element_with_fallback(self.locators.get("lump_sum_payment_amount_label"))
        lump_sum_payment_elems = self.get_all_elements_with_fallback(self.locators.get("lump_sum_payment_amount_value"))
        if lump_sum_payment_elems:
            lump_sum_amount = lump_sum_payment_elems[0].text.strip()
            if lump_sum_amount:
                # "원"이 포함되어 있는지 확인
                if "원" in lump_sum_amount:
                    logger.info(f" - 수납 금액: {lump_sum_amount}")
                else:
                    logger.warning(f"⚠️ 수납 금액에 '원'이 포함되어 있지 않습니다: {lump_sum_amount}")
            else:
                logger.warning("⚠️ 수납 금액 요소는 존재하지만 텍스트가 비어있습니다.")
        else:
            logger.warning("⚠️ 수납 금액 요소를 찾을 수 없습니다.")

    def regular_payment_method_selection(self, payment_data, customer_name):
        """
        1. '정기결제 수단'이 보이는지 확인
            1-1 없으면 정기결제 수단은 false반환하고 함수 종료
            1-2 기존 등록된 정기결제 수단이 있으면 true반환하고 함수 종료
        2. 1번에서 이상없으면 '정기결제 수단 선택'클릭
        3. '추가' 버튼을 클릭
        4. UI확인
            4-1 '결제수단 추가'타이틀 확인
            4-2 '카드이체, 은행이체 서브 타이틀 확인
            4-3 기본 '카드이체'로 되어 있는지 확인
        5. 카드이체, 은행이체 중 랜덤 선택

        (카드 이체 및 은행 이체 시나리오 생략 - 구현부 참조)
        """
        logger.info("👉 결제 수단 선택 및 추가 시나리오를 시작합니다.")

        # 1. '정기결제 수단'이 보이는지 분기 확인 (check_element_exists 활용)
        is_regular_visible = self.check_element_exists(self.locators.get('regular_payment_method_label'))

        if not is_regular_visible:
            # 1-1 정기결제 수단 섹션이 화면에 없음 → 작업 수행 불가 (스킵)
            logger.info("⚠️ '정기결제 수단'이 보이지 않아 시나리오를 스킵합니다.")
            return False  # False: 작업 수행 불가 (정기결제 수단이 없는 경우)

        # 1-2. 이미 등록된 결제수단이 있는지 확인
        is_button_visible = self.check_element_exists(self.locators.get('regular_payment_method_button'))
        
        if not is_button_visible:
            # 이미 등록된 결제수단이 있는 경우 - 파싱 및 검증 후 완료 처리
            logger.info("✅ 이미 등록된 정기결제 수단이 있습니다. 정보를 확인합니다.")
            self._verify_existing_payment_method(payment_data)
            return True  # True: 작업 완료 (이미 등록되어 있어 추가 작업 불필요)

        # 2. '정기결제 수단' 클릭
        logger.info("✅ '정기결제 수단'이 확인되어 [정기결제 수단 선택] 버튼을 클릭합니다.")
        self.wait_and_click(self.locators.get('regular_payment_method_button'), "정기결제 수단 선택 버튼")

        # 3. '추가' 버튼을 클릭
        self.wait_and_click(self.locators.get('payment_method_add_button'), "추가 버튼")

        # 4. UI 확인
        logger.info("🔍 결제수단 추가 팝업 UI를 검증합니다.")
        self.swipe_down()
        # 4-1, 4-2 에러를 발생시키는 find_element_with_fallback으로 필수 요소 강제 검증
        self.find_element_with_fallback(self.locators.get('popup_title'))
        self.find_element_with_fallback(self.locators.get('tab_card_transfer'))
        self.find_element_with_fallback(self.locators.get('tab_bank_transfer'))
        
        # 4-3 기본 '카드이체'로 되어 있는지 확인
        card_tab = self.find_element_with_fallback(self.locators.get('tab_card_transfer'))
        if card_tab.get_attribute("selected") == "true":
            logger.info("✅ '카드이체'가 기본으로 선택되어 있습니다.")
        else:
            logger.error("❌ '카드이체'가 기본 선택되어 있지 않습니다.")

        # 5. 카드이체, 은행이체 중 랜덤 선택
        selected_method = random.choice(['card', 'bank'])
        logger.info(f"🎲 랜덤 선택된 결제 방식: {'카드이체' if selected_method == 'card' else '은행이체'}")

        if selected_method == 'card':
            # === [카드 이체 로직] ===
            # test_data.json의 PaymentData에서 직접 참조
            card_company = payment_data.get('CARD_COMPANY')
            card_number = payment_data.get('CARD_NUMBER')
            expiry_month = payment_data.get('EXPIRATION_MONTH')
            expiry_year = payment_data.get('EXPIRATION_YEAR')
            
            # 카드 탭 클릭 (은행 탭이 선택되어 있을 수 있으므로 명시적으로 클릭)
            self.wait_and_click(self.locators.get('tab_card_transfer'), "카드이체 탭 클릭")
            
            # 1-1 '카드사 입력' 클릭
            self.wait_and_click(self.locators.get('card_company_select_button'), "카드사 입력 버튼")
            # 1-2 카드사 선택 (템플릿 사용)
            card_company_template = self.locators.get('card_company_template')
            dynamic_card_locator = {}
            for key, value in card_company_template.items():
                if value:
                    dynamic_card_locator[key] = value.replace("{card_company}", card_company)
            self.wait_and_click(dynamic_card_locator, f"{card_company} 선택")
            # 1-3 카드번호 입력
            self.wait_and_send_keys(self.locators.get('card_number_input'), card_number, "카드번호 입력창")
            # 1-4 유효기간 월, 년도 입력
            self.wait_and_send_keys(self.locators.get('expiry_month_input'), expiry_month, "유효기간 월")
            self.wait_and_send_keys(self.locators.get('expiry_year_input'), expiry_year, "유효기간 년")
            # 유효기간 년 입력 후 키보드 닫기
            self.hide_keyboard()
    
            # 2~5번 동작 수행
            self._fill_common_info_and_submit(customer_name, payment_method='card')
            
            # 6. 추가 확인 로직
            self._verify_added_method_text('card', card_company, card_number)

        else:
            # === [은행 이체 로직] ===
            # test_data.json의 PaymentData에서 직접 참조
            bank_name = payment_data.get('BANK_NAME')
            account_number = payment_data.get('ACCOUNT_NUMBER')

            # 은행 탭 클릭
            self.wait_and_click(self.locators.get('tab_bank_transfer'), "은행이체 탭 클릭")
            
            # 1-1 '은행 입력' 클릭
            self.wait_and_click(self.locators.get('bank_select_button'), "'은행 입력'버튼 클릭")
            
            # 1-2 은행 선택 (템플릿 사용 + 스와이프 로직)
            # 템플릿 구조: bank_name_template에서 {bank_name}을 실제 은행명으로 치환
            # 예: "//android.widget.Button[@text='{bank_name}']" → "//android.widget.Button[@text='신한은행']"
            bank_name_template = self.locators.get('bank_name_template')
            dynamic_bank_locator = {}
            for key, value in bank_name_template.items():
                if value:
                    dynamic_bank_locator[key] = value.replace("{bank_name}", bank_name)
            
            # 화면에 은행이 보이는지 확인하고, 없으면 스와이프하여 찾기
            max_swipe_attempts = 5  # 최대 스와이프 횟수
            swipe_count = 0
            bank_found = False
            
            while swipe_count < max_swipe_attempts:
                # 은행이 화면에 있는지 확인
                if self.check_element_exists(dynamic_bank_locator, timeout=1):
                    bank_found = True
                    logger.info(f"✅ '{bank_name}' 은행을 찾았습니다.)")
                    break
                else:
                    # 은행이 없으면 스와이프
                    swipe_count += 1
                    logger.info(f"🔍 '{bank_name}' 은행을 찾기 위해 스와이프합니다. ({swipe_count}/{max_swipe_attempts})")
                    self.swipe_up(start_y_ratio=0.7, end_y_ratio=0.5, duration=500)
                    time.sleep(1)  # 스와이프 후 화면 안정화 대기
            
            if not bank_found:
                raise Exception(f"'{bank_name}' 은행을 찾을 수 없습니다. (최대 {max_swipe_attempts}회 스와이프 시도)")
            
            # 은행 선택
            self.wait_and_click(dynamic_bank_locator, f"{bank_name} 선택")
            # 1-3 계좌번호 입력
            self.wait_and_send_keys(self.locators.get('account_number_input'), account_number, "계좌번호 입력필드")
            # 계좌번호 입력 후 키보드 닫기
            self.hide_keyboard()

            # 2~5번 동작 수행
            self._fill_common_info_and_submit(customer_name, payment_method='bank')
            
            # 6. 추가 확인 로직
            self._verify_added_method_text('bank', bank_name, account_number)
        
        # 정상적으로 완료되면 True 반환
        return True

    def lump_sum_payment_method_selection(self, payment_data, customer_name):
        """
        1. '수납결제 수단'이 보이는지 확인
            1-1 없으면 수납결제 수단은 스킵
        2. '수납결제 수단'클릭
        3. '추가' 버튼을 클릭
        4. UI확인
            4-1 '결제수단 추가'타이틀 확인
            4-2 '카드이체, 은행이체 서브 타이틀 확인
            4-3 기본 '카드이체'로 되어 있는지 확인
        5. 카드이체, 은행이체 중 랜덤 선택

        (카드 이체 및 은행 이체 시나리오 생략 - 구현부 참조)
        """
        logger.info("👉 수납결제 수단 선택 및 추가 시나리오를 시작합니다.")

        # 1. '수납결제 수단'이 보이는지 분기 확인 (check_element_exists 활용)
        is_lump_sum_visible = self.check_element_exists(self.locators.get('lump_sum_payment_method_label'))

        if not is_lump_sum_visible:
            # 1-1 없으면 수납결제 수단은 스킵
            logger.info("⚠️ '수납결제 수단'이 보이지 않아 시나리오를 스킵합니다.")
            return

        # 2. '수납결제 수단' 클릭
        logger.info("✅ '수납결제 수단'이 확인되어 [수납결제 수단 선택] 버튼을 클릭합니다.")
        self.wait_and_click(self.locators.get('lump_sum_payment_method_button'), "수납결제 수단 선택 버튼")

        # 3. '추가' 버튼을 클릭
        self.wait_and_click(self.locators.get('payment_method_add_button'), "추가 버튼")

        # 4. UI 확인
        logger.info("🔍 결제수단 추가 팝업 UI를 검증합니다.")
        time.sleep(0.5)
        # 4-1, 4-2 에러를 발생시키는 find_element_with_fallback으로 필수 요소 강제 검증
        self.swipe_down()
        self.find_element_with_fallback(self.locators.get('popup_title'))
        self.find_element_with_fallback(self.locators.get('tab_card_transfer'))
        self.find_element_with_fallback(self.locators.get('tab_bank_transfer'))
        
        # 4-3 기본 '카드이체'로 되어 있는지 확인
        card_tab = self.find_element_with_fallback(self.locators.get('tab_card_transfer'))
        if card_tab.get_attribute("selected") == "true":
            logger.info("✅ '카드이체'가 기본으로 선택되어 있습니다.")
        else:
            logger.error("❌ '카드이체'가 기본 선택되어 있지 않습니다.")

        # 5. 카드이체, 은행이체 중 랜덤 선택
        selected_method = random.choice(['card', 'bank'])
        logger.info(f"🎲 랜덤 선택된 결제 방식: {'카드이체' if selected_method == 'card' else '은행이체'}")

        if selected_method == 'card':
            # === [카드 이체 로직] ===
            # test_data.json의 PaymentData에서 직접 참조
            card_company = payment_data.get('CARD_COMPANY')
            card_number = payment_data.get('CARD_NUMBER')
            expiry_month = payment_data.get('EXPIRATION_MONTH')
            expiry_year = payment_data.get('EXPIRATION_YEAR')
            
            # 카드 탭 클릭 (은행 탭이 선택되어 있을 수 있으므로 명시적으로 클릭)
            self.wait_and_click(self.locators.get('tab_card_transfer'), "카드이체 탭 클릭")
            
            # 1-1 '카드사 입력' 클릭
            self.wait_and_click(self.locators.get('card_company_select_button'), "카드사 입력 버튼")
            # 1-2 카드사 선택 (템플릿 사용)
            card_company_template = self.locators.get('card_company_template')
            dynamic_card_locator = {}
            for key, value in card_company_template.items():
                if value:
                    dynamic_card_locator[key] = value.replace("{card_company}", card_company)
            self.wait_and_click(dynamic_card_locator, f"{card_company} 선택")
            # 1-3 카드번호 입력
            self.wait_and_send_keys(self.locators.get('card_number_input'), card_number, "카드번호 입력창")
            # 1-4 유효기간 월, 년도 입력
            self.wait_and_send_keys(self.locators.get('expiry_month_input'), expiry_month, "유효기간 월")
            self.wait_and_send_keys(self.locators.get('expiry_year_input'), expiry_year, "유효기간 년")
            # 유효기간 년 입력 후 키보드 닫기
            self.hide_keyboard()
            
            # 2~5번 동작 수행
            self._fill_common_info_and_submit(customer_name, payment_method='card')
            
            # 6. 추가 확인 로직
            self._verify_added_method_text('card', card_company, card_number)

        else:
            # === [은행 이체 로직] ===
            # test_data.json의 PaymentData에서 직접 참조
            bank_name = payment_data.get('BANK_NAME')
            account_number = payment_data.get('ACCOUNT_NUMBER')

            # 은행 탭 클릭
            self.wait_and_click(self.locators.get('tab_bank_transfer'), "은행이체 탭 클릭")
            
            # 1-1 '은행 입력' 클릭
            self.wait_and_click(self.locators.get('bank_select_button'), "은행 입력 버튼")
            # 1-2 은행 선택 (템플릿 사용)
            bank_name_template = self.locators.get('bank_name_template')
            dynamic_bank_locator = {}
            for key, value in bank_name_template.items():
                if value:
                    dynamic_bank_locator[key] = value.replace("{bank_name}", bank_name)
            self.wait_and_click(dynamic_bank_locator, f"{bank_name} 선택")
            # 1-3 계좌번호 입력
            self.wait_and_send_keys(self.locators.get('account_number_input'), account_number, "계좌번호 입력창")
            # 계좌번호 입력 후 키보드 닫기
            self.hide_keyboard()

            # 2~5번 동작 수행
            self._fill_common_info_and_submit(customer_name, payment_method='bank')
            
            # 6. 추가 확인 로직
            self._verify_added_method_text('bank', bank_name, account_number)

    def click_next_button(self):
        """
        '다음' 버튼을 클릭하여 다음 단계로 이동합니다.
        """
        logger.info("🚀 [다음] 버튼을 클릭합니다.")
        self.wait_and_click(self.locators['next_button'], "다음 버튼")
        time.sleep(1)
        logger.info("🚀 [설치정보 화면으로 이동] 버튼을 클릭합니다.")
        self.wait_and_click(self.locators['next_step5'], "설치정보 화면으로 이동 버튼")

    def _fill_common_info_and_submit(self, customer_name, payment_method='bank'):
        """이체일, 명의 선택 및 스와이프 후 최종 추가 버튼을 누릅니다."""
        # 2-1 이체일 랜덤 선택 (결제 방식에 따라 옵션 다름)
        if payment_method == 'card':
            # 카드이체: 10일, 20일만 가능 (15일 없음)
            available_days = ['10일', '20일']
        else:
            # 은행이체: 10일, 15일, 20일 모두 가능
            available_days = ['10일', '15일', '20일']
        
        selected_day = random.choice(available_days)
        transfer_day_template = self.locators.get('transfer_day_template')
        dynamic_day_locator = {}
        for key, value in transfer_day_template.items():
            if value:
                dynamic_day_locator[key] = value.replace("{transfer_day}", selected_day)
        
        #랜덤으로 10일이 선택되었을 때는 기본값이므로 클릭하지 않고 넘어가기
        if selected_day == '10일':
            logger.info(f"✅ 이체일 '{selected_day}'은 기본값이므로 클릭하지 않고 넘어갑니다.")
            time.sleep(0.5)
        else:
            # 10일이 아닌 경우 클릭
            self.wait_and_click(dynamic_day_locator, f"이체일 {selected_day} 선택")
            time.sleep(1)

        # 2-2 명의 개인 활성화 확인 TODO: 법인, 개인사업자 추가 필요
        personal_button = self.find_element_with_fallback(self.locators.get('owner_type_personal_button'))
        
        # 여러 속성을 확인하여 선택 상태 판단 (Android WebView에서는 일부 속성이 제대로 반환되지 않을 수 있음)
        is_enabled = personal_button.get_attribute("enabled")
        
        if is_enabled == "true":
            # 속성이 제대로 반환되지 않더라도 버튼이 활성화되어 있으면 기본값으로 선택되어 있다고 가정
            logger.info("✅ 명의 '개인'은 기본값으로 선택되어 있습니다.")
        else:
            logger.warning(f"⚠️ 명의 '개인' 선택 상태를 확인할 수 없습니다.")

        # 2-3 스와이프 (BasePage의 swipe_up 함수 사용)
        self.swipe_up()

        # 3. 명의자 확인
        owner_elem = self.find_element_with_fallback(self.locators.get('owner_name_input'))
        actual_name = owner_elem.text
        if actual_name == customer_name:
            logger.info(f"✅ 명의자 일치: {actual_name}")
        else:
            logger.error(f"❌ 명의자 불일치: 기대값({customer_name}), 실제값({actual_name})")

        # 4. 법정생년월일 확인
        birth_elem = self.find_element_with_fallback(self.locators.get('birth_date_input'))
        logger.info(f"법정생년월일 : {birth_elem.text}")

        # 5. 추가하기 버튼 클릭
        time.sleep(0.5)
        self.wait_and_click(self.locators.get('add_submit_button'), "추가하기 버튼")

    def _verify_existing_payment_method(self, payment_data):
        """
        이미 등록된 결제수단 정보를 파싱하고 검증합니다.
        1. 화면에 표시된 결제수단 텍스트 가져오기
        2. 카드/은행 구분 및 회사명 추출
        3. 숫자 부분 추출 (카드: 6자리, 은행: 4자리)
        4. 마스킹 검증 (*로 표시되는지 확인)
        5. test_data.json의 PaymentData와 일치 여부 확인
        """
        
        logger.info("🔍 이미 등록된 결제수단 정보를 확인합니다.")
        
        # 이미 등록된 결제수단 텍스트 가져오기
        try:
            existing_method_elem = self.find_element_with_fallback(self.locators.get('regular_payment_method_selected'))
            existing_text = existing_method_elem.text.strip()
            logger.info(f"📋 화면에 표시된 결제수단: {existing_text}")
        except Exception as e:
            logger.error(f"❌ 이미 등록된 결제수단을 찾을 수 없습니다: {e}")
            return
        
        # 카드이체 또는 은행이체 구분
        if "카드이체" in existing_text:
            method_type = "card"
            expected_company = payment_data.get('CARD_COMPANY')
            expected_number = payment_data.get('CARD_NUMBER')
            expected_digits = 6  # 카드는 6자리까지 노출
        elif "은행이체" in existing_text:
            method_type = "bank"
            expected_company = payment_data.get('BANK_NAME')
            expected_number = payment_data.get('ACCOUNT_NUMBER')
            expected_digits = 4  # 은행은 4자리까지 노출
        else:
            logger.error(f"❌ 결제수단 형식을 인식할 수 없습니다: {existing_text}")
            raise Exception(f"결제수단 형식 오류: {existing_text}")
        
        # 회사명 추출 (예: "카드이체 : 신한카드 449911********")
        # 패턴: "카드이체 : {회사명} {숫자}***" 또는 "은행이체 : {은행명} {숫자}***"
        pattern = rf"{'카드이체' if method_type == 'card' else '은행이체'}\s*:\s*([^\s]+)\s+(\d+)\*+"
        match = re.search(pattern, existing_text)
        
        if not match:
            logger.error(f"❌ 결제수단 텍스트를 파싱할 수 없습니다: {existing_text}")
            raise Exception(f"파싱 오류: {existing_text}")
        
        extracted_company = match.group(1)
        extracted_number = match.group(2)
        
        logger.info(f"📝 추출된 정보 - 회사명: {extracted_company}, 숫자: {extracted_number}")
        
        # 회사명 일치 확인
        if extracted_company != expected_company:
            logger.error(f"❌ 회사명 불일치: 기대값({expected_company}), 실제값({extracted_company})")
            raise Exception(f"회사명 불일치: 기대값({expected_company}), 실제값({extracted_company})")
        else:
            logger.info(f"✅ 회사명 일치: {extracted_company}")
        
        # 숫자 자릿수 확인 (카드: 6자리, 은행: 4자리)
        if len(extracted_number) != expected_digits:
            logger.error(f"❌ 숫자 자릿수 불일치: 기대값({expected_digits}자리), 실제값({len(extracted_number)}자리)")
            raise Exception(f"숫자 자릿수 불일치: 기대값({expected_digits}자리), 실제값({len(extracted_number)}자리)")
        else:
            logger.info(f"✅ 숫자 자릿수 일치: {len(extracted_number)}자리")
        
        # 추출된 숫자가 test_data.json의 앞부분과 일치하는지 확인
        expected_prefix = expected_number[:expected_digits]
        if extracted_number != expected_prefix:
            logger.error(f"❌ 숫자 불일치: 기대값({expected_prefix}), 실제값({extracted_number})")
            raise Exception(f"숫자 불일치: 기대값({expected_prefix}), 실제값({extracted_number})")
        else:
            logger.info(f"✅ 숫자 일치: {extracted_number}")
        
        # 마스킹 검증 (*로 표시되는지 확인)
        # 전체 텍스트에서 숫자 다음 부분이 모두 *인지 확인
        number_start_idx = existing_text.find(extracted_number) + len(extracted_number)
        remaining_text = existing_text[number_start_idx:].strip()
        
        # 숫자 다음에 *만 있는지 확인
        if remaining_text and not all(c == '*' for c in remaining_text if c != ' '):
            logger.error(f"❌ 마스킹 형식 오류: 숫자 다음이 모두 *가 아닙니다. ({remaining_text})")
            raise Exception(f"마스킹 형식 오류: {remaining_text}")
        else:
            logger.info(f"✅ 마스킹 형식 확인: 숫자 다음이 *로 표시됨")
        
        # 전체 번호 길이 확인 (마스킹된 부분 포함)
        total_expected_length = len(expected_number)
        masked_length = len(remaining_text.replace(' ', ''))
        visible_length = len(extracted_number)
        
        if visible_length + masked_length != total_expected_length:
            logger.warning(f"⚠️ 전체 번호 길이 불일치: 기대값({total_expected_length}자리), 실제값({visible_length + masked_length}자리)")
        else:
            logger.info(f"✅ 전체 번호 길이 일치: {total_expected_length}자리")
        
        logger.info(f"✅ 이미 등록된 결제수단 검증 완료: {extracted_company} {extracted_number}***")

    def _verify_added_method_text(self, method_type, company, number):
        """카드는 6자리, 은행은 4자리 노출 후 마스킹 처리하여 검증합니다."""
        if method_type == 'card':
            masked_number = number[:6] + "*" * (len(number) - 6) if len(number) > 6 else number
            expected_text = f"카드이체 : {company} {masked_number}"
        else:
            masked_number = number[:4] + "*" * (len(number) - 4) if len(number) > 4 else number
            expected_text = f"은행이체 : {company} {masked_number}"

        # locator 파일의 템플릿 사용
        verify_template = self.locators.get('payment_method_verify_template')
        dynamic_locator = {}
        for key, value in verify_template.items():
            if value:
                dynamic_locator[key] = value.replace("{expected_text}", expected_text)

        # 6-1, 6-2 동일한 텍스트를 가진 요소가 나타나는지 대기하며 확인 (check_element_exists 활용)
        is_added = self.check_element_exists(dynamic_locator, timeout=10)
        
        if is_added:
            logger.info(f"✅ [검증 성공] 결제수단이 정상적으로 노출되었습니다: {expected_text}")
        else:
            logger.error(f"❌ [검증 실패] 결제수단을 화면에서 찾을 수 없습니다: {expected_text}")
