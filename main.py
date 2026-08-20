import sys
import time
from pynput.keyboard import Controller, Key

keyboard = Controller()

LAST_SEEN = {}
DUPLICATE_DELAY = 3.0  # 3초 내 동일 태그 중복 입력 방지

def calculate_ean13_check_digit(digits_12_str):
    """
    12자리 숫자 스트링을 받아 GS1 표준 체크디지트(13번째 자리) 계산
    - 홀수 인덱스(1, 3, 5, 7, 9, 11번째) * 3
    - 짝수 인덱스(0, 2, 4, 6, 8, 10번째) * 1
    """
    odd_sum = sum(int(digits_12_str[i]) for i in range(1, 12, 2))
    even_sum = sum(int(digits_12_str[i]) for i in range(0, 12, 2))
    
    total = (odd_sum * 3) + even_sum
    check_digit = (10 - (total % 10)) % 10
    return str(check_digit)

def sgtin96_to_ean13(hex_str):
    """SGTIN-96 EPC Hex 데이터를 13자리 EAN-13으로 완벽 변환"""
    try:
        hex_str = hex_str.strip()
        if len(hex_str) != 24:
            return None
        
        # Hex -> 96비트 이진수 변환
        bin_str = bin(int(hex_str, 16))[2:].zfill(96)
        
        # Header 0x30 (00110000) 검증
        if bin_str[:8] != '00110000':
            return None
            
        partition = int(bin_str[11:14], 2)
        
        # GS1 SGTIN-96 Partition Table
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
        
        # SGTIN-96 표준 조합:
        # Indicator(Item Ref 첫 자리) + Company Prefix + Item Ref 나머지 자리 = 정확히 12자리
        indicator = item_ref[0]
        item_number = item_ref[1:]
        
        digits_12 = indicator + company_prefix + item_number
        
        # 12자리 데이터 기반으로 13번째 체크디지트 계산
        check_digit = calculate_ean13_check_digit(digits_12)
        
        # 최종 13자리 EAN-13 출력
        return digits_12 + check_digit

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
    
    print(f"[Sequential HID Typed] {ean_code}")
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
                print(f"변환 결과: {ean13}")
                time.sleep(0.5) 
                type_sequentially(ean13)
            else:
                print("유효하지 않은 SGTIN-96 Hex 포맷입니다.\n")
                
        except (EOFError, KeyboardInterrupt):
            break
