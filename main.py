import sys
import time
from pynput.keyboard import Controller, Key

keyboard = Controller()

LAST_SEEN = {}
DUPLICATE_DELAY = 3.0  # 3초 내 동일 태그 중복 입력 방지

def calculate_check_digit(digits_str):
    """GS1 표준 체크디지트 계산 (GTIN-13/14 공용)"""
    # 오른쪽에서부터 역순으로 3, 1, 3, 1... 가중치 적용
    reversed_digits = digits_str[::-1]
    total = 0
    for idx, digit in enumerate(reversed_digits):
        weight = 3 if idx % 2 == 0 else 1
        total += int(digit) * weight
        
    return str((10 - (total % 10)) % 10)

def sgtin96_to_ean13(hex_str):
    """SGTIN-96 Hex를 13자리 EAN-13으로 변환"""
    try:
        hex_str = hex_str.strip()
        if len(hex_str) != 24:
            return None
        
        # Hex -> 96비트 이진수 변환
        bin_str = bin(int(hex_str, 16))[2:].zfill(96)
        
        # Header 0x30 검증
        if bin_str[:8] != '00110000':
            return None
            
        partition = int(bin_str[11:14], 2)
        
        partition_table = {
            0: (40, 12, 4, 1),
            1: (37, 11, 7, 2),
            2: (34, 10, 10, 3),
            3: (30, 9, 14, 4),
            4: (27, 8, 17, 5),
            5: (24, 7, 20, 6),
            6: (20, 6, 24, 7)
        }
        
        if partition not in partition_table:
            return None
            
        m_bits, m_digits, l_bits, l_digits = partition_table[partition]
        
        company_bits = bin_str[14 : 14 + m_bits]
        item_bits = bin_str[14 + m_bits : 14 + m_bits + l_bits]
        
        company_prefix = str(int(company_bits, 2)).zfill(m_digits)
        item_ref = str(int(item_bits, 2)).zfill(l_digits)
        
        # Indicator(1자리) + Company Prefix + Item Ref 나머지
        indicator = item_ref[0]
        item_number = item_ref[1:]
        
        # 13자리 Payload 생성 (GTIN-14의 체크디지트 제외 부분)
        payload13 = indicator + company_prefix + item_number
        
        # 체크디지트 계산하여 14자리 GTIN 생성
        check_digit = calculate_check_digit(payload13)
        gtin14 = payload13 + check_digit
        
        # 맨 앞 '0'을 뗀 13자리 EAN-13 반환
        if gtin14.startswith('0'):
            return gtin14[1:]
        return gtin14

    except Exception:
        return None

def type_sequentially(ean_code):
    """한 글자씩 순차 기입 (HID)"""
    current_time = time.time()
    
    if ean_code in LAST_SEEN and (current_time - LAST_SEEN[ean_code]) < DUPLICATE_DELAY:
        return False
        
    LAST_SEEN[ean_code] = current_time
    
    for char in ean_code:
        keyboard.press(char)
        keyboard.release(char)
        time.sleep(0.03)  # 30ms 지연
        
    time.sleep(0.05)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    
    print(f"[HID Typed] {ean_code}")
    return True

if __name__ == "__main__":
    print("--- Zebra FXP20 EAN-13 HID Injector ---")
    
    while True:
        try:
            hex_input = input("Hex EPC 스캔/입력: ")
            if hex_input.lower() == 'q':
                break
                
            ean13 = sgtin96_to_ean13(hex_input)
            
            if ean13:
                print(f"변환 결과 (EAN-13): {ean13}")
                time.sleep(0.5) 
                type_sequentially(ean13)
            else:
                print("유효하지 않은 SGTIN-96 Hex 포맷입니다.\n")
                
        except (EOFError, KeyboardInterrupt):
            break
