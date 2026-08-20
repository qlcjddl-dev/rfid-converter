const epcTds = require('epc-tds');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function convertHexToEan(hexStr) {
  try {
    let epc = epcTds.valueOf(hexStr.trim());
    let gtin = epc.getGtin(); // GTIN 값 가져오기
    
    // 맨 앞의 '0'을 제거하여 13자리 EAN 형태로 변환
    if (gtin && gtin.startsWith('0')) {
      return gtin.substring(1);
    }
    return gtin;
  } catch (e) {
    return "Error: " + e.message;
  }
}

console.log("--- RFID Hex to EAN Converter (Node.js) ---");
rl.question("Enter Hex EPC: ", (hexInput) => {
  let result = convertHexToEan(hexInput);
  console.log(Result EAN-13: ${result});
  rl.close();
});
