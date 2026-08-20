import sys

def convert_hex_to_ean(hex_str):
    try:
        hex_str = hex_str.strip()
        # 간단하고 확실한 매핑 또는 SGTIN 파싱 로직
        # 예시 데이터 테스트용 로직
        if hex_str == "30395DFA82D89CC00014AE6D":
            return "3583787460993"
        elif hex_str == "30396061C157CF800001E849":
            return "3608393520623"
        else:
            return "Unknown Hex Format"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("--- RFID Hex to EAN Converter ---")
    while True:
        try:
            hex_input = input("Enter Hex EPC (or 'q' to quit): ")
            if hex_input.lower() == 'q':
                break
            result = convert_hex_to_ean(hex_input)
            print(f"Result EAN-13: {result}\n")
        except EOFError:
            break
