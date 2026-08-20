import sys
import time
from pynput.keyboard import Controller, Key

keyboard = Controller()

LAST_SEEN = {}
DUPLICATE_DELAY = 3.0  # 3초 내 동일 태그 중복 입력 방지

def sgtin96_to_ean13(hex_str):
    """SGTIN-96 EPC Hex 데이터를 EAN-13으로 변환"""
    try:
        hex_str = hex_str.strip()
        if len(hex_str) != 24:
            return None
        
        bin_str = bin(int(hex_str, 16))[2:].zfill(96)
        if bin_str[:8] != '00110000': # Header 0x30
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
        
        gtin12 = item_ref[0] + company_prefix + item_ref[1:]
        
        odds = sum(int(gtin12[i]) for i in range(0, 12, 2))
        evens = sum(int(gtin12[i]) for i in range(1, 12, 2))
        check_digit = (10 - ((odds + (evens * 3)) % 10)) % 10
        
        return gtin12 + str(check_digit)
    except Exception:
        return None

def type_sequentially(ean_code):
    """한글 조합 및 타이핑 씹힘 방지를 위한 1글자씩 순차 기입"""
    current_time = time.time()
    
    # 3초 내 동일 태그 중복 실행 차단 (1회만 타이핑)
    if ean_code in LAST_SEEN and (current_time - LAST_SEEN[ean_code]) < DUPLICATE_DELAY:
        return False
        
    LAST_SEEN[ean_code] = current_time
    
    # 한 글자씩 순서대로 Key Down / Up 이벤트 발생
    for char in ean_code:
        keyboard.press(char)
        keyboard.release(char)
        time.sleep(0.03)  # 30ms 지연 (한글 전환 문제 및 타이핑 오작동 방지)
        
    # 기입 완료 후 Enter 1회 입력
    time.sleep(0.05)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    
    print(f"[Sequential HID Typed] {ean_code}")
    return True

if __name__ == "__main__":
    print("--- Zebra FXP20 Sequential HID Injector ---")
    
    while True:
        try:
            hex_input = input("Hex EPC 스캔/입력: ")
            if hex_input.lower() == 'q':
                break
                
            ean13 = sgtin96_to_ean13(hex_input)
            
            if ean13:
                # 스캔받은 터미널 창에서 원하는 입력창(메모장/ERP 등)으로 
                # 커서를 옮길 수 있도록 0.5초 대기 후 순차 기입 시작
                time.sleep(0.5) 
                type_sequentially(ean13)
            else:
                print("유효하지 않은 SGTIN-96 Hex 포맷입니다.\n")
                
        except (EOFError, KeyboardInterrupt):
            break
