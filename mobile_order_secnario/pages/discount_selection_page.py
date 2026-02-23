from pages.base_page import BasePage
from utils.locator_manager import locator_manager
from utils.logger import logger
import random
import re

class DiscountSelectionPage(BasePage):
    """
    모바일 주문의 '할인 선택(Step3)' 페이지를 나타내는 클래스입니다.
    """

    def __init__(self, driver, platform):
        super().__init__(driver, platform)
        locator_manager.set_platform(platform)
        self.locators = locator_manager.get_locators("discount_select")

    # ⬇️ [추가] 페이지 진입 후 주요 요소(Step, Title, 고객명) 검증 함수
    def verify_page_components(self, expected_customer_name, expected_total_count):
        """
        할인 선택 페이지의 주요 요소를 검증합니다.
        1. page Title확인(할인 선택)
        2. step3에 맞게 3으로 되어 있는지 확인
        :param expected_customer_name: 검증할 고객 이름
        :param expected_total_count: 검증할 총 주문 개수
        """
        logger.info("🔍 할인 선택 페이지 진입 검증을 시작합니다.")

        try:
            # 1. Page Title 검증 ('할인 선택')
            title_element = self.find_element_with_fallback(self.locators.get("page_title"))
            title_text = title_element.text
            if "할인 선택" not in title_text:
                raise Exception(f"페이지 타이틀 불일치: 기대값 '할인 선택', 실제값 '{title_text}'")
            logger.info(f"✅ Page Title 확인 완료: {title_text}")

            # 2. Step Indicator 검증 ('3')
            step_element = self.find_element_with_fallback(self.locators.get("step_indicator"))
            step_text = step_element.text
            if "3" != step_text:
                raise Exception(f"Step 단계 불일치: 기대값 '3', 실제값 '{step_text}'")
            logger.info(f"✅ Step 단계 확인 완료: {step_text}단계")

            # 3. Customer Name 검증 (예: '고객명: 음규환')
            customer_element = self.find_element_with_fallback(self.locators.get("customer_name"))
            customer_text = customer_element.text
            if expected_customer_name not in customer_text:
                 raise Exception(f"고객명 불일치: '{expected_customer_name}'가 '{customer_text}'에 없음")
            logger.info(f"✅ 고객명 정보 확인 완료: {customer_text}")

            # 4. 주문 갯수 확인
            total_element = self.find_element_with_fallback(self.locators.get("total_count"))
            total_text = total_element.text
            numbers = re.findall(r'\d+', total_text)
            
            if not numbers:
                raise Exception(f"총 주문 건수 텍스트에서 숫자를 찾을 수 없습니다: '{total_text}'")
                
            actual_count = int(numbers[0]) # 추출한 첫 번째 숫자를 정수로 변환
            
            if expected_total_count != actual_count:
                raise Exception(f"총 주문 건수 불일치: 기대값 '{expected_total_count}', 실제값 '{actual_count}' (텍스트: {total_text})")
                
            logger.info(f"✅ 총 주문 건수 확인 완료: {actual_count}개")
            logger.info("🎉 [Pass] 할인 선택 페이지의 모든 요소가 정상입니다.")


        except Exception as e:
            logger.error(f"❌ 할인 선택 페이지 검증 실패: {e}")
            self.take_screenshot("discount_page_verification_failure")
            raise

            
    def check_simultaneous_discount(self, product_count):
            """
            주문 상품 개수에 따라 동시구매할인 활성화 여부를 확인합니다.
            
            시나리오
            1. 제품이 1개인지 2개이상인지 확인
            2. 제품이 1개일 때 
                2-1 동 설정 비활성화 확인
                2-2 동시구매 상태가 적용불가로 표기되는지 확인
            3. 제품이 2개이상일 때 
                3-1 동시구매 설정 활성화 확인
                3-2 동시구매 상태가 "미적용", "할인율%"로 노출 상태 확인

            param 정의
                product_count: 담은 상품 개수 (int)
            """
            logger.info(f"🔍 동시구매할인 조건 확인 시작 (상품 수: {product_count}개)")
            try:
                setting_btn = self.find_element_with_fallback(self.locators.get("simultaneous_discount_setting"))
                is_enabled = setting_btn.get_attribute("enabled") == "true"
                status_element = self.find_element_with_fallback(self.locators.get("simultaneous_discount_status"))
                simultaneous_status = status_element.text
                if product_count >= 2:
                    if is_enabled:
                        logger.info("✅ 상품이 2개 이상이므로 동시구매할인 설정이 '활성화'되어 있습니다. (정상)")

                    else:
                        logger.warning("⚠️ 상품이 2개 이상이나 동시구매할인 설정이 '비활성화' 상태입니다.")

                    if "미적용" in simultaneous_status:
                        logger.info("✅ 동시구매 미적용 상태입니다.")
                    elif "%" in simultaneous_status: 
                        match = re.search(r'([-\d]+)%', simultaneous_status)
                        if match:
                            discount_rate = match.group(1)
                            logger.info(f"✅ 동시구매할인이 적용되었습니다. 할인율: {discount_rate}%")
                        else:
                            logger.warning(f"⚠️ '%' 기호는 있지만 숫자를 인식할 수 없습니다: {simultaneous_status}")
                    else:
                        logger.warning(f"⚠️ 상태 텍스트가 예상('미적용' or '%')과 다릅니다: '{simultaneous_status}'")
                else:
                    if not is_enabled:
                        logger.info("✅ 상품이 1개이므로 동시구매할인 설정이 '비활성화'되어 있습니다. (정상)")
                    else:
                        logger.warning("❌ 상품이 1개인데 동시구매할인 설정이 '활성화'되어 있습니다.")

                    # 1개일 때는 '적용 불가' 텍스트인지 추가 확인
                    if "적용불가" in simultaneous_status:
                        logger.info("✅ 동시구매할인 상태가 '적용불가'로 정상 표시되었습니다.")
                    else:
                        logger.warning(f"⚠️ 상품이 1개인데 상태 텍스트가 '{simultaneous_status}'입니다.")    

            except Exception as e:
                logger.error(f"❌ 동시구매할인 확인 중 오류: {e}")
                self.take_screenshot("simultaneous_discount_check_failure")
                raise

    def check_and_configure_combination_discount(self):
        """
        결합할인이 활성화되어 있는지 확인하고, 활성화 시 설정을 진행합니다.(결합할인 조건=> 30일 이내 주문 건 존재)
        시나리오
            1. 결합할인이 적용가능한지 확인
            2. 결합할인이 불가한 경우
                2-1 결합할인 설정 비활성화 확인
                2-2 결합할인 상태가 적용불가로 표기되는지 확인
            3. 결합할인이 가능한 경우
                3-1 결합할인 설정 활성화 확인
                3-2 결합할인 상태가 "미적용", "할인율%"로 노출 상태 확인

        """
        logger.info("🔍 결합할인 활성화 여부 확인 및 설정 시도")
        try:
            
            setting_btn = self.find_element_with_fallback(self.locators.get("combination_discount_setting"))
            status_element = self.find_element_with_fallback(self.locators.get("combination_discount_status"))
            combination_status = status_element.text
            
            is_enabled = setting_btn.get_attribute("enabled") == "true"

            if is_enabled:
                logger.info("✨ 결합할인이 설정이 활성화되어 있습니다.")
                
                if "%" in combination_status:       # 할인이 적용된 상태
                    match = re.search(r'([-\d]+)%', combination_status)
                    if match:
                        discount_rate = match.group(1)
                        logger.info(f"✅ 결합할인이 적용되었습니다. 할인율: {discount_rate}%")
                    else:
                        logger.warning(f"⚠️ '%' 기호는 있지만 숫자를 인식할 수 없습니다: {combination_status}")
                    
                elif "미적용" in combination_status:    #미적용된 상태 
                    logger.info("✅ 결합할인 '미적용' 상태입니다.")
                
                else:                               # 활성화인데 '적용불가'나 엉뚱한 텍스트가 뜨면 경고
                    logger.warning(f"⚠️ [오류] 설정은 활성화되어 있으나, 상태 텍스트가 정상 범위(%, 미적용)가 아닙니다: '{combination_status}'")
                
                # TODO: 결합할인 설정 팝업 로직 구현 필요 
                # self.handle_popup_selection()
                
            else:
                logger.info("ℹ️ 결합할인이 설정이 바활성화되어 있습니다.")
            
                if "적용불가" in combination_status:
                    logger.info("✅ 결합할인 '적용불가' 상태입니다. (조건 미충족)")
                else:
                    # 비활성화인데 '미적용'이나 '%'가 뜨면 논리적 오류
                    logger.warning(f"⚠️ [오류] 설정이 비활성화 상태인데, 텍스트가 '적용불가'가 아닙니다: '{combination_status}'")
            
        except Exception as e:
            logger.error(f"❌ 결합할인 확인/설정 중 오류: {e}")
            self.take_screenshot("combination_discount_error")
            # 비활성화 확인 실패는 치명적이지 않을 수 있으므로 pass 혹은 raise 결정
            pass

    def get_regular_payment_discount(self):
        """
        정기결제할인이 존재하면 금액을 추출하여 반환합니다.
        시나리오
        1. 정기결제할인이 있는지 확인
            1-1 정기결제할인이 있으면 할인 금액만 추출하여 변수에 저장
            1-2 화면 내 요소(정기결제)가 없으면 스와이프(1회)진행 후 1-1다시 진행
        2. 최종 정기결제할인이 없으면 None(할인없는 것으로 스킵)
        :return: 할인 금액 문자열 (예: "-1,000원/월") 또는 None
        """
        logger.info("🔍 정기결제할인 정보 확인")
        try:
            # 1. '정기결제할인' 텍스트가 포함된 버튼 찾기
            element = self.find_element_with_fallback(self.locators.get("regular_payment_discount"))
        except:
            self.swipe_up()
            try:
                # [2차 시도] 스크롤 후 다시 찾기
                element = self.find_element_with_fallback(
                    self.locators.get("regular_payment_discount"), timeout=1
                )
            except:
                # [2차 실패] 스크롤 해도 없음 -> 할인 대상 아님으로 해당 함수 종료
                logger.info("ℹ️ 정기결제할인 대상이 아닙니다 (요소 없음).")
                return None
        
            # --- 요소 발견 성공 시 텍스트 분석 ---
        try:
            full_text = element.text
            logger.info(f"📌 발견된 텍스트: '{full_text}'")
            
            # 텍스트에서 금액 추출 (예: "정기결제할인 -1,000원/월" -> "-1,000원/월")
            match = re.search(r'([-\d,]+원(?:/월)?)', full_text)
            
            if match:
                discount_amount = match.group(1)
                logger.info(f"💰 정기결제할인 금액 : {discount_amount}")
                return discount_amount
            else:
                logger.warning(f"⚠️ 정기결제할인 버튼은 찾았으나 금액 형식을 인식 못함: {full_text}")
                return full_text
                
        except Exception as e:
            logger.error(f"❌ 텍스트 분석 중 오류: {e}")
            return None

    def get_prepass_discount(self): #TODO : 탭해서 팝업 랜덤선택 구현 필요
        """
        Pre-Pass 할인이 존재하면 금액을 추출하여 반환합니다.
        시나리오
        1. Pre-Pass 할인이 있는지 확인
            1-1 Pre-Pass 할인이 있으면 할인 금액만 추출하여 변수에 저장
            1-2 화면 내 요소가 없으면 스와이프(1회) 진행 후 1-1 다시 진행
        2. 최종 Pre-Pass 할인이 없으면 None (할인 없는 것으로 스킵)
        :return: 할인 금액 문자열 (예: "-100,000원") 또는 None
        """
        logger.info("🔍 Pre-Pass 할인 정보 확인")

        # 1. 요소가 있는지 조용히 확인 (에러 로그 없이)
        if not self.check_element_exists(self.locators.get("pre_pass_discount"), timeout=2):
            # 화면에 안 보임 -> 스크롤 1회 수행 후 재확인
            self.swipe_up()
            if not self.check_element_exists(self.locators.get("pre_pass_discount"), timeout=1):
                # 스크롤 해도 없음 -> 할인 대상 아님 (정상적인 경우)
                logger.info("ℹ️ Pre-Pass 할인 대상이 아닙니다 (요소 없음).")
                return None
        
        # 2. 요소가 존재하는 것이 확인되었으므로 안전하게 찾기
        try:
            element = self.find_element_with_fallback(self.locators.get("pre_pass_discount"))
        except Exception as e:
            # 예상치 못한 오류 발생 시
            logger.warning(f"⚠️ Pre-Pass 요소 확인 후 찾기 실패: {e}")
            return None

        # --- 요소 발견 성공 시 텍스트 분석 --- TODO : 프리패스 랜덤 적용 추가 필요
        try:
            full_text = element.text
            logger.info(f"📌 발견된 텍스트: '{full_text}'")

            # 텍스트에서 금액 추출 (예: "등록비-100,000원" -> "-100,000원")
            # 정기결제와 동일한 Regex 패턴 사용 (숫자+원)
            match = re.search(r'([-\d,]+원(?:/월)?)', full_text)

            if match:
                discount_amount = match.group(1)
                logger.info(f"💰 Pre-Pass 할인 금액 : {discount_amount}")
                return discount_amount
            else:
                logger.warning(f"⚠️ Pre-Pass 버튼은 찾았으나 금액 형식을 인식 못함: {full_text}")
                return full_text

        except Exception as e:
            logger.error(f"❌ 텍스트 분석 중 오류: {e}")
            return None

    def get_rental_fee_agreement_discount(self):
        """
        렌탈료약정할인 프로그램이 존재하면 금액을 추출하여 반환합니다.
        시나리오
        1. 렌탈료약정할인이 있는지 확인 (XPath contains 사용)
            1-1 있으면 할인 금액만 추출하여 변수에 저장
            1-2 화면 내 요소가 없으면 스와이프(1회) 진행 후 1-1 다시 진행
        2. 최종적으로 없으면 None (할인 없는 것으로 스킵)
        :return: 할인 금액 문자열 (예: "-4,000원/월") 또는 None
        """
        logger.info("🔍 렌탈료약정할인 프로그램 정보 확인")
        import re

        try:
            # 1. '렌탈료약정할인 프로그램' 텍스트가 포함된 버튼 찾기 (1차 시도)
            element = self.find_element_with_fallback(self.locators.get("rental_fee_agreement_discount"))
        except:
            # [1차 실패] 화면에 안 보임 -> 스크롤 1회 수행
            self.swipe_up(start_y_ratio=0.7, end_y_ratio=0.4)   #30%로만 스와이프
            try:
                # [2차 시도] 스크롤 후 다시 찾기 (Timeout 1초)
                element = self.find_element_with_fallback(
                    self.locators.get("rental_fee_agreement_discount"), timeout=1
                )
            except:
                # [2차 실패] 스크롤 해도 없음 -> 할인 대상 아님
                logger.info("ℹ️ 렌탈료약정할인 프로그램 대상이 아닙니다 (요소 없음).")
                return None

        # --- 요소 발견 성공 시 텍스트 분석 ---
        try:
            full_text = element.text
            logger.info(f"📌 발견된 텍스트: '{full_text}'")

            # 텍스트에서 금액 추출
            # 예: "렌탈료약정할인 프로그램 -4,000 원/월" -> "-4,000 원/월"
            # (공백 \s?를 추가하여 '-4,000원'과 '-4,000 원' 모두 대응하도록 함)
            match = re.search(r'([-\d,]+\s?원(?:/월)?)', full_text)

            if match:
                discount_amount = match.group(1)
                logger.info(f"💰 렌탈료약정할인 금액 : {discount_amount}")
                return discount_amount
            else:
                logger.warning(f"⚠️ 버튼은 찾았으나 금액 형식을 인식 못함: {full_text}")
                return full_text

        except Exception as e:
            logger.error(f"❌ 텍스트 분석 중 오류: {e}")
            return None

    def select_prepayment_discount_option(self):
        """
        선납 할인 선택 로직을 수행합니다.
        시나리오:
        1. 선납 할인 버튼이 있는지 확인
            1-1 없으면 스킵
        2. 클릭 후 팝업 종류(경고 vs 선택) 확인
            2-1 선택 팝업창일 때 : 랜덤 선택 후 결과 저장
            2-2 경고 팝업창일 때 : 경고 문구 저장 후 닫기
        3. 2-1에서 선택한 옵션과 선택 후 노출되는 상태값 결과가 같은지 확인 ("1년 +0원 할인 적용" 형식 확인)
        """
        logger.info("🔍 선납 할인 적용 가능 여부 확인")

        try:
            # 1. 선납 할인 버튼 확인 (없으면 함수 종료)
            try:
                self.swipe_up(start_y_ratio=0.7, end_y_ratio=0.5)
                trigger_btn = self.find_element_with_fallback(
                    self.locators.get("prepayment_discount_trigger"))
            except:
                logger.info("ℹ️ 선납 할인 선택 메뉴가 없습니다.")
                return

            # 2. 버튼 클릭 (팝업 호출)
            trigger_btn.click()
            logger.info("👆 선납 할인 버튼 클릭 완료")

            # 3. 팝업 확인 (경고 팝업인지, 선택 팝업인지 분기 처리)
            # 약간의 딜레이 후 경고 메시지가 먼저 뜨는지 확인
            try:
                # [Case A] 선택 불가 (경고 팝업 발생)
                warning_element = self.find_element_with_fallback(
                    self.locators.get("prepayment_warning_msg"), timeout=2
                )
                warning_text = warning_element.text
                logger.warning(f"⚠️ 선납 할인 적용 불가: {warning_text}")
                
                # 확인 버튼 눌러서 닫기
                confirm_btn = self.find_element_with_fallback(self.locators.get("warning_confirm_btn"))
                confirm_btn.click()
                logger.info("Pop-up 닫기 완료. 선납할인 검증을 종료합니다.")
                return # 함수 종료
                
            except:
                pass    # 경고 없으면 선택 팝업으로 진행

            # [Case B] 선택 가능 (선택 팝업 진입)
            try:
                # 팝업 제목 확인
                title_element = self.find_element_with_fallback(self.locators.get("prepayment_popup_title"), timeout=4)
                logger.info(f"✅ 적용 가능 팝업 진입 : {title_element.text}")
                
                # 4. 랜덤 선택 로직
                available_options = []
                
                # 검사할 옵션 리스트 (키 이름)
                option_keys = [
                    "prepayment_option_none", 
                    "prepayment_option_1y", 
                    "prepayment_option_2y", 
                    "prepayment_option_3y"
                ]
                
                # 화면에 실제로 존재하는 옵션만 리스트에 담기
                for key in option_keys:
                    try:
                        # timeout을 짧게 주어 빠르게 검사
                        opt = self.find_element_with_fallback(self.locators.get(key), timeout=1)
                        available_options.append(opt)
                    except:
                        continue # 없으면 패스

                if not available_options:
                    logger.warning("⚠️ 선택 가능한 옵션이 없습니다.")
                    return

                # 랜덤 선택
                selected_element = random.choice(available_options)
                selected_text = selected_element.text
                
                logger.info(f"🎲 랜덤 선택된 옵션: '{selected_text}'")
                selected_element.click()

                # 1. 결과 요소 찾기 (화면에 적용된 텍스트)
                # 예: "1년 + 272,290 (-17,390원 할인 적용)"
                result_element = self.find_element_with_fallback(
                    self.locators.get("prepayment_discount_result"))
                result_text = result_element.text
                logger.info(f"📌 [화면 노출 값] : '{result_text}'")

                # 2. 정규표현식으로 3가지 정보 분리 추출
                # Group 1: 년수 (맨 앞부분)
                # Group 2: 선납금액 (+ 기호 포함)
                # Group 3: 할인금액 (- 기호 포함, 괄호 안)
                pattern = r"^(.*?)\s*([+\-]\s*[\d,]+).*?\(([-\d,]+)원"
                
                match = re.search(pattern, result_text)
                
                if match:
                    # 추출 (공백 제거 포함)
                    extracted_year = match.group(1).strip()      # "1년"
                    prepayment_amount = match.group(2).strip()   # "+ 272,290"
                    discount_amount = match.group(3).strip()     # "-17,390"
                    
                    # 3. [검증] 팝업에서 선택한 값 vs 화면에 찍힌 년수 비교
                    if selected_text == extracted_year:
                        logger.info(f"✅ [Pass] 년수가 정확히 일치합니다: {extracted_year}")
                        # 4. 선납금액, 할인금액 정보 출력
                        logger.info(f"   ℹ️ 선납 금액: {prepayment_amount}")
                        logger.info(f"   ℹ️ 할인 금액: {discount_amount}원")
                    else:
                        logger.error("❌ [Fail] 선택한 년수와 화면 표시 년수가 다릅니다!")
                        logger.error(f"   - 선택한 값: '{selected_text}'")
                        logger.error(f"   - 화면 추출: '{extracted_year}'")
                        
                else:
                    logger.error(f"❌ 텍스트 형식을 파싱할 수 없습니다. 실제 텍스트: {result_text}")

            except Exception as e:
                logger.error(f"❌ 선납 할인 선택 및 검증 중 오류: {e}")
                pass

        except Exception as e:
            logger.error(f"❌ 선납 할인 로직 전체 오류: {e}")
            pass


    def check_and_select_prepayment2_discount(self):
        """
        선납할인2 선택 로직을 수행합니다.
        시나리오:
        1. 선납할인2 버튼 존재 여부 확인
            1-1 선납할인2 버튼 없으면 함수 종료
        2. 클릭 후 팝업 종류(경고 vs 선택) 확인
            2-1 선택 팝업창일 때 : 랜덤 선택 후 결과 저장
                팝업 내 '/월'이 포함된 모든 옵션을 수집
                랜덤 선택 후 값(선납금액, 할인금액) 파싱
            2-2 경고 팝업창일 때 : 경고 문구 저장 후 닫기
        3. 현재 상태값 결과 텍스트 확인 ("x원 선납 (-y원 할인 적용") 형식 확인)
        """
        logger.info("🔍 선납할인2 적용 가능 여부 확인")

        try:
            # 1. 선납할인2 버튼 확인 (없으면 함수 종료)
            try:
                self.swipe_up(start_y_ratio=0.7, end_y_ratio=0.5)
                trigger_btn = self.find_element_with_fallback(
                    self.locators.get("prepayment2_discount_trigger"))
                current_text = trigger_btn.text
                logger.info(f"📌 [선납할인2] 현재 상태: {current_text}")
            except:
                logger.info("ℹ️ 선납할인2 메뉴가 없습니다.")
                return

            # 2. 선납할인2가 있으면 버튼 클릭 (팝업 호출)
            trigger_btn.click()
            logger.info("👆 선납할인2 버튼 클릭 완료")

            # 3. 경고 팝업 체크 (선택 불가 케이스 처리)
            try:
                warning = self.find_element_with_fallback(
                    self.locators.get("prepayment_warning_msg"), timeout=1.5
                )
                logger.warning(f"⚠️ [선납할인2] 적용 불가 사유: {warning.text}")
                
                # 확인 버튼 눌러서 닫기
                self.find_element_with_fallback(self.locators.get("warning_confirm_btn")).click()
                logger.info("   -> 경고 팝업을 닫고 기존 상태를 유지합니다.")
                return 
            except: #경고 팝업 미노출 시 선납할인2 팝업 노출 확인시도로 이동
                pass # 경고 없으면 정상 진행

            # 4. 선납할인2 팝업 확인 후, 모든 옵션 리스트 가져와서 랜덤 선택
            try:
                # 팝업 제목 확인 (선택 팝업인지 확인용)
                self.find_element_with_fallback(self.locators.get("prepayment_discount2_popup_title"), timeout=2)
                options_list = self.get_all_elements_with_fallback(self.locators.get("prepayment2_options"))
            except:
                logger.error("❌ 선납할인2 팝업 확인 실패")
                return
                
            if not options_list:
                logger.warning("⚠️ 선납할인2에 선택 가능한 옵션이 하나도 없습니다.")
                return

            # 발견된 옵션 목록 추출 (중복 제거 및 필터링)
            options_text_list = []
            seen_texts = set()
            unique_options_list = []
            
            for elem in options_list:
                text = elem.text.strip()
                if text and text not in seen_texts:
                    # 선납할인2 팝업 내부의 옵션만 포함
                    if text == "선납할인2 할인 선택 없음" or (text.count("원") >= 2 and "/월" in text):
                        seen_texts.add(text)
                        options_text_list.append(text)
                        unique_options_list.append(elem)
            
            logger.info(f"📋 발견된 옵션 목록 ({len(unique_options_list)}개): {options_text_list}")
            
            # 필터링된 리스트로 교체
            options_list = unique_options_list

            # 5. 랜덤 선택
            selected_element = random.choice(options_list)
            selected_text = selected_element.text.strip()
            logger.info(f"🎲 랜덤 선택한 옵션: '{selected_text}'")

            # 6. [데이터 파싱] 선택한 값이 '선택 없음'인지 '금액'인지 분석
            is_no_selection = "선택 없음" in selected_text
            
            expected_prepay = ""
            expected_discount = ""

            if not is_no_selection:
                # [Case A] 금액 옵션 선택 시 (예: "500,000 원 -952원/월" 또는 "1,000,000원 -1,905원/월")
                # 실제 형식: "선납금액 원 할인금액원/월" (첫 번째 "원" 앞에 공백이 있을 수 있음)
                # 패턴: 선납금액 + 공백(선택) + "원" + 공백(선택) + 할인금액 + "원/월"
                match = re.search(r"([\d,]+)\s*원\s*([-\d,]+)원/월", selected_text)
                if match:
                    expected_prepay = match.group(1)   # 예: "1,000,000"
                    expected_discount = match.group(2) # 예: "-1,905"
                    logger.info(f"   ㄴ [Expected] 선납: {expected_prepay}, 할인: {expected_discount}")
                else:
                    # 정규표현식 매칭 실패 시 경고 로그 출력
                    logger.warning(f"⚠️ 선택한 옵션 텍스트를 파싱할 수 없습니다: '{selected_text}'")
                    logger.warning(f"   ㄴ 예상 형식: '+ 1,000,000원 선납 (-1,905원 할인 적용)'")

            else:
                # [Case B] '선택 없음' 선택 시
                logger.info("   ㄴ '선납할인2 할인 선택 없음'을 선택했습니다.")

            # 7. 클릭하여 적용
            selected_element.click()

            # -------------------------------------------------------
            # 8. [결과 검증] 결과 화면 텍스트 확인
            # -------------------------------------------------------
            logger.info("🔍 적용 결과 확인")
            
            # 결과 요소 다시 찾기 (텍스트가 변경되었을 것임)
            result_element = self.find_element_with_fallback(
                self.locators.get("prepayment2_discount_trigger"), timeout=3
            )
            result_text = result_element.text
            logger.info(f"📌 [Actual] 화면 노출 값: '{result_text}'")

            if is_no_selection:
                # [검증 A] '선택 없음' 선택 시 -> '선택 없음' 텍스트나 기본 메뉴명('선납할인2')이 보여야 함
                if "선택 없음" in result_text or "선납할인2" in result_text:
                    logger.info("✅ [Pass] '선납할인2 할인 선택 없음' 상태가 정상적으로 적용되었습니다.")
                else:
                    logger.error(f"❌ [Fail] 초기화되지 않았습니다. 실제값: {result_text}")
            else:
                # [검증 B] 금액 선택 시 -> 선택한 금액 숫자가 결과 텍스트에 포함되어 있는지 확인
                # 결과 텍스트 형식: "+ 500,000원 선납 (-952원 할인 적용)"
                # 선택한 값의 숫자("500,000"과 "-952")가 결과 텍스트에 포함되어 있으면 Pass
                if expected_prepay in result_text and expected_discount in result_text:
                    logger.info("✅ [Pass] 선택한 금액이 결과 화면에 정확히 반영되었습니다.")
                    logger.info(f"   - 선택한 값: {expected_prepay}원 선납, {expected_discount}원/월 할인")
                    logger.info(f"   - 화면 표시: {result_text}")
                else:
                    logger.error("❌ [Fail] 선택한 값과 결과 값이 다릅니다.")
                    logger.error(f"   - 기대값: 선납 {expected_prepay} / 할인 {expected_discount}")
                    logger.error(f"   - 실제값: {result_text}")

        except Exception as e:
            logger.error(f"❌ [선납할인2] 로직 수행 중 오류 발생: {e}")
     
    def verify_price_calculation_logic(self):
        """
        [최적화] 금액 계산 및 상품 합계 검증 로직
        1. 각 항목(상품, 할인, 총액)의 우측 모든 형제 요소를 가져옵니다.
        2. 내부 파싱 함수에서 다음 섹션 라벨(예: '할인금액')을 만나면 파싱을 중단합니다.
        3. 추출된 금액으로 (상품 + 할인 == 총액) 공식을 검증합니다.
        """
        logger.info("💰 금액 계산 및 상품 합계 검증 시작")

        try:
            # ---------------------------------------------------------
            # [Helper] 텍스트 파싱 및 값 추출 내부 함수
            # ---------------------------------------------------------
            def parse_price_data(elements, label_name):
                x_text, y_text = "미노출", "미노출"
                x_val, y_val = 0, 0

                if not elements:
                    logger.warning(f"⚠️ [{label_name}] 요소를 찾지 못했습니다 (0원 처리).")
                    return x_val, y_val

                for elem in elements:
                    try:
                        text = elem.text.strip()
                        if not text: continue
                        
                        # [Case A] 월 렌탈료 (예: "33,400원/월")
                        if "원/월" in text:
                            match = re.search(r'([-\d,]+)원/월', text)
                            if match:
                                y_text = match.group(0)
                                y_val = int(match.group(1).replace(',', ''))
                            continue

                        # [Case B] 수납/등록비 (예: "수납 100,000원", "0원")
                        if "원" in text and "/월" not in text:
                            match = re.search(r'(?:수납\s*)?([-\d,]+)원', text)
                            if match:
                                x_text = match.group(0) if "수납" in text else match.group(1) + "원"
                                x_val = int(match.group(1).replace(',', ''))
                                
                    except Exception:
                        pass # 파싱 에러 무시

                logger.info(f"   👉 [{label_name}] 파싱 결과: 수납='{x_text}'({x_val}), 월='{y_text}'({y_val})")
                return x_val, y_val

            # ---------------------------------------------------------
            # 1. 데이터 수집 및 파싱 (XPath가 정확한 요소만 리턴함)
            # ---------------------------------------------------------
            
            # [상품 금액]
            self.find_element_with_fallback(self.locators.get("product_amount_label"))
            product_elems = self.get_all_elements_with_fallback(self.locators.get("product_amount_value"))
            prod_x, prod_y = parse_price_data(product_elems, "상품금액")
            
            # [할인 금액]
            self.find_element_with_fallback(self.locators.get("discount_amount_label"))
            discount_elems = self.get_all_elements_with_fallback(self.locators.get("discount_amount_value"))
            disc_x, disc_y = parse_price_data(discount_elems, "할인금액")
            
            # [총 금액]
            self.find_element_with_fallback(self.locators.get("total_amount_label"))
            total_elems = self.get_all_elements_with_fallback(self.locators.get("total_amount_value"))
            total_x, total_y = parse_price_data(total_elems, "총 금액")

            # ---------------------------------------------------------
            # 2. 검증 (상품 + 할인 = 총액)
            # ---------------------------------------------------------
            calc_x = prod_x + disc_x
            calc_y = prod_y + disc_y

            logger.info(f"📊 검증식 [수납]: {prod_x} + ({disc_x}) = {calc_x} (화면값: {total_x})")
            logger.info(f"📊 검증식 [월]  : {prod_y} + ({disc_y}) = {calc_y} (화면값: {total_y})")

            # [수납 금액 검증]
            if calc_x != total_x:
                logger.error(f"❌ 수납 금액 불일치! 계산: {calc_x}, 화면: {total_x}")
            else:
                logger.info(f"✅ [Pass] 수납 금액 일치: {total_x}원")
            
            # [월 금액 검증]
            if calc_y != total_y:
                logger.error(f"❌ 월 금액 불일치! 계산: {calc_y}, 화면: {total_y}")
            else:
                logger.info(f"✅ [Pass] 월 금액 일치: {total_y}원")

            logger.info("🏁 금액 계산 검증 로직 종료")

        except Exception as e:
            logger.error(f"❌ 금액 검증 중 치명적 오류: {e}", exc_info=True)
            self.take_screenshot("price_verification_fatal_error")
            return

    def click_next_button(self):
        """
        다음 버튼 클릭 및 주문 확인 팝업 처리 함수
        
        시나리오:
        1. '다음' 버튼 클릭 (화면 하단 스크롤 포함)
        2. 주문 확인 팝업(예: "주문1", "주문2"...) 노출 여부 확인
            2-1. 팝업이 뜨면 -> '확인' 버튼 클릭
            2-2. 팝업이 안 뜨면 -> 그대로 진행 (Skip)
        3. step4이동 확인(상단 4확인)
        """
        try:
            # 1. 다음 버튼 클릭
            self.wait_and_click(self.locators.get("next_button"), "다음 버튼")
            logger.info("👆 [다음] 버튼 클릭 완료")
            
            # 2. 팝업 처리 (조건부 실행)
            # 팝업이 뜰 수도 있고 안 뜰 수도 있으므로, check_element_exists로 안전하게 확인 (대기 2초)
            popup_confirm_locator = self.locators.get("order_confirmation_popup_confirm_btn")
            
            if self.check_element_exists(popup_confirm_locator, timeout=2):
                logger.info("🔔 주문 확인 팝업이 감지되었습니다.")
                
                # 확인 버튼 클릭
                self.wait_and_click(popup_confirm_locator, "주문 확인 팝업 '확인' 버튼")
                logger.info("✅ 팝업 '확인' 버튼 클릭 완료 -> 다음 단계로 진행")
            else:
                logger.info("ℹ️ 주문 확인 팝업이 뜨지 않았습니다. (바로 다음 단계 진행)")
            
        except Exception as e:
            logger.error(f"❌ 다음 버튼 클릭 또는 팝업 처리 중 오류 발생: {e}")
            self.take_screenshot("next_button_failure")
            return

        try:
            # 1. 다음 버튼 클릭 후 step4이동 확인
            self.find_element_with_fallback(self.locators.get("payment_info_select"))
            logger.info("step4이동 완료")
            logger.info("✅ [Step3] 테스트가 완료되었습니다.")
        except Exception as e:
            logger.error(f"❌ 다음 버튼 클릭 또는 팝업 처리 중 오류 발생: {e}")
            self.take_screenshot("step4이동 불가 에러")