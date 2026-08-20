import sys
import time
from pynput.keyboard import Controller, Key

keyboard = Controller()

LAST_SEEN = {}
DUPLICATE_DELAY = 3.0  # 3초 내 동일 태그 중복 입력 방지

def calculate_ean13_check_digit(gtin12_str):
    """
    GTIN-12 스트링을 입력받아 올바른 EAN-13 체크디지트(13번째 자리) 계산
    GS1 표준 알고리즘:
    - 0-indexed 기준: 홀수 인덱스(1,3,5,7,9,11) 값들의 합 * 3
    - 짝수 인덱스(0,2,4,6,8,10) 값들의 합 * 1
    """
    odd_sum = sum(int(gtin12_str[i]) for i in range(1, 12, 2))   # 2, 4, 6, 8, 10, 12번째 자리
    even_sum = sum(int(gtin12_str[i]) for i in range(0, 12, 2))  # 1, 3, 5, 7, 9, 11번째 자리
    
    total = (odd_sum * 3) + even_sum
    check_digit = (10 - (total % 10)) % 10
    return str(check_digit)

def sgtin96_to_ean13(hex_str):
    """SGTIN-96 EPC Hex 데이터를 정확한 EAN-13으로 변환"""
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
        partition_table = {
            0: (40, 12, 4, 1), 1: (37, 11, 7, 2), 2: (34, 10, 10, 3),
            3: (30, 9, 14, 4), 4: (27, 8, 17, 5), 5: (24, 7, 20, 6),
            6: (20, 6, 24, 7)
        }
        
        if partition not in partition_table:
            return None
            
        m_bits, m_digits, l_bits, l_digits = partition_table[partition]
        
        company_prefix = str(int(bin_str[14 : 14 + m_bits], 2)).zfill(m_digits)
        item_ref = str(int(bin_str[14 + m_bits : 14 + m_bits + l_bits], 2)).zfill(l_digits)
        
        # GTIN-12 조합: Item Ref의 첫 자리가 Indicator(구분자)
        gtin12 = item_ref[0] + company_prefix + item_ref[1:]
        
        # 정확한 체크디지트 계산 후 결합
        check_digit = calculate_ean13_check_digit(gtin12)
        return gtin12 + check_digit

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
    print("--- Zebra FXP20 Fixed EAN-13 Injector ---")
    
    # 올바른 결과 검증 예시
    # 30395DFA82D89CC00014AE6D -> 3583787460993
    # 30396061C157CF800001E849 -> 3608393520623
    
    while True:
        try:
            hex_input = input("Hex EPC 스캔/입력: ")
            if hex_input.lower() == 'q':
                break
                
            ean13 = sgtin96_to_ean13(hex_input)
            
            if ean13:
                print(f"변환 결과 EAN-13: {ean13}")
                time.sleep(0.5) 
                type_sequentially(ean13)
            else:
                print("유효하지 않은 SGTIN-96 Hex 포맷입니다.\n")
                
        except (EOFError, KeyboardInterrupt):
            break
