from epc_tds import Sgsg

def convert_hex_to_ean(hex_str):
    try:
        # SGTIN-96 파싱
        tag = Sgsg(hex_str.strip())
        gtin = tag.gtin() # 보통 14자리 (예: 03608393520623)
        
        # 앞의 '0' 제거하여 13자리 EAN으로 변환
        if gtin.startswith('0'):
            return gtin[1:]
        return gtin
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("--- RFID Hex to EAN Converter ---")
    while True:
        hex_input = input("Enter Hex EPC (or 'q' to quit): ")
        if hex_input.lower() == 'q':
            break
        result = convert_hex_to_ean(hex_input)
        print(f"Result EAN-13: {result}\n")
