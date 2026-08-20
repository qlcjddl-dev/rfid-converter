const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Hex(SGTIN-96)를 EAN-13으로 변환하는 순수 함수
function convertHexToEan(hexStr) {
  try {
    hexStr = hexStr.trim();
    // 16진수 문자열을 바이너리 비트 스트링으로 변환
    let binStr = "";
    for (let i = 0; i < hexStr.length; i++) {
      let val = parseInt(hexStr[i], 16).toString(2).padStart(4, '0');
      binStr += val;
    }

    // SGTIN-96 구조 분석 (Partition은 38~40번째 비트)
    // 파티션 값에 따라 Company Prefix와 Item Reference의 비트 길이가 달라짐
    let partition = parseInt(binStr.substr(38, 3), 2);
    
    // 파티션별 컴퍼니 프리픽스 비트 수 표에 따른 처리
    // 표준적인 SGTIN-96 변환 로직 적용
    let companyPrefixBits = [40, 37, 34, 30, 27, 24, 20];
    let indicatorBits = 3;
    
    let cpBitLen = companyPrefixBits[partition];
    let itemRefBitLen = 44 - cpBitLen; // Item Reference + Indicator 총 44비트 중 Indicator 제외
    
    // 이진 데이터에서 컴퍼니 프리픽스와 품목 코드 추출 위치
    // (시작점: Header(8) + Type(2) + Filter(3) + Partition(3) = 16비트 이후부터)
    let pos = 16;
    let indicator = parseInt(binStr.substr(pos, indicatorBits), 2);
    pos += indicatorBits;
    
    let companyPrefix = parseInt(binStr.substr(pos, cpBitLen), 2).toString();
    pos += cpBitLen;
    
    let itemReference = parseInt(binStr.substr(pos, itemRefBitLen), 2).toString();
    
    // 자릿수 패딩 맞추기 (Indicator + Company Prefix + Item Reference = 13자리 GTIN-13)
    let rawGtin = indicator.toString() + companyPrefix.padStart(12 - indicator.toString().length - companyPrefix.length, '0') + itemReference;
    
    // 만약 계산된 결과가 14자리이거나 앞에 0이 붙는다면 13자리 EAN으로 맞춤
    let fullGtin = rawGtin.padStart(13, '0');
    if (fullGtin.length > 13 && fullGtin.startsWith('0')) {
      fullGtin = fullGtin.substring(1);
    }
    
    return fullGtin;
  } catch (e) {
    // 만약 표준 디코딩 외에 입력된 데이터 매핑이 필요할 경우의 예외 처리
    return "Conversion Error: " + e.message;
  }
}

console.log("--- RFID Hex to EAN Converter ---");
rl.question("Enter Hex EPC: ", (hexInput) => {
  let result = convertHexToEan(hexInput);
  console.log(Result EAN-13: ${result});
  rl.close();
});
