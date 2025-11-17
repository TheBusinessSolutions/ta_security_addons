function numberToWords(number) {
    const units = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
        'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
    const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
    const scales = ['', 'Thousand', 'Million', 'Billion', 'Trillion', 'Quadrillion', 'Quintillion'];

    function convertLessThanThousand(num) {
        if (num === 0) return '';
        if (num < 20) return units[num];
        if (num < 100) return tens[Math.floor(num / 10)] + (num % 10 ? '-' + units[num % 10] : '');
        return units[Math.floor(num / 100)] + ' Hundred' + (num % 100 ? ' and ' + convertLessThanThousand(num % 100) : '');
    }

    function convertWholeNumber(num) {
        if (num === 0) return 'Zero';

        let result = '';
        let scaleIndex = 0;

        while (num > 0) {
            if (num % 1000 !== 0) {
                let chunk = convertLessThanThousand(num % 1000);
                // 只在最后一个三位数中保留 "and"
                if (scaleIndex > 0) {
                    chunk = chunk.replace(' and ', ' ');
                }
                result = chunk + (scales[scaleIndex] ? ' ' + scales[scaleIndex] + ' ' : '') + result;
            }
            num = Math.floor(num / 1000);
            scaleIndex++;
        }

        return result.trim();
    }

    function convertDecimals(decimal) {
        let result = '';
        for (let digit of decimal) {
            result += ' ' + units[parseInt(digit)];
        }
        return result.trim();
    }

    // 处理0
    if (number === 0) return 'Zero';

    // 使用toFixed保持原始小数位数
    let [intPart, decimalPart] = number.toFixed(Math.max(0, number.toString().split('.')[1]?.length || 0)).split('.');
    intPart = parseInt(intPart);

    // 处理整数部分
    let result = convertWholeNumber(intPart);

    // 处理小数部分
    if (decimalPart) {
        result += ' Point ' + convertDecimals(decimalPart);
    }

    return result;
}
