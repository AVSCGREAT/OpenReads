import Quagga from 'quagga';  // barcode scanning library
import LazyBookCard from './LazyBookCard';

const BOX_STYLE = {color: 'green', lineWidth: 2};
const RESULT_BOX_STYLE = {color: 'blue', lineWidth: 2};
const RESULT_LINE_STYLE = {color: 'red', lineWidth: 15};

export function init() {
    Quagga.init({
        inputStream: {
            name: 'Live',
            type: 'LiveStream',
            target: $('#interactive')[0],
        },
        decoder: {
            readers: ['ean_reader'],
            multiple: false
        },
    }, function(err) {
        if (err) throw err;
        Quagga.start();
    });

    Quagga.onProcessed(result => {
        if (!result) return;

        const drawingCtx = Quagga.canvas.ctx.overlay;
        const drawingCanvas = Quagga.canvas.dom.overlay;

        if (result.boxes) {
            const canvasWidth = parseFloat(drawingCanvas.getAttribute('width'));
            const canvasHeight = parseFloat(drawingCanvas.getAttribute('height'));
            drawingCtx.clearRect(0, 0, canvasWidth, canvasHeight);

            result.boxes.forEach(box => {
                if (box != result.box) {
                    Quagga.ImageDebug.drawPath(box, {x: 0, y: 1}, drawingCtx, BOX_STYLE);
                }
            });
        }

        if (result.box) {
            Quagga.ImageDebug.drawPath(result.box, {x: 0, y: 1}, drawingCtx, RESULT_BOX_STYLE);
        }

        if (result.codeResult && result.codeResult.code && isBarcodeISBN(result.codeResult.code)) {
            Quagga.ImageDebug.drawPath(result.line, {x: 'x', y: 'y'}, drawingCtx, RESULT_LINE_STYLE);
        }
    });

    let lastResult = null;
    let confirmation_list = [];
    Quagga.onDetected(result => {
        const code = result.codeResult.code;
        const url = `/isbn/${code}`;

        if (!isBarcodeISBN(code) || code == lastResult) return;
        lastResult = code;

        if (isBarcodeISBN(code) && document.getElementById('multiple-scan').checked == false){
            if (CheckISBN(code, confirmation_list) == true)
                window.location.href= url;
        }
        const isbn = code;
        const canvas = Quagga.canvas.dom.image;
        const card = LazyBookCard.fromISBN(isbn);
        card.updateState({coverSrc: canvas.toDataURL()});
        $('#result-strip').prepend(card.render());
    });
}

/**
 * Check if scanned code is an isbn
 * @param {string} code
 * @return {Boolean}
 */
function isBarcodeISBN(code) {
    return code.startsWith('97');
}

function CheckISBN(code, confirmation_list) {
    if (confirmation_list.length == 0) {
        confirmation_list.push(code);
    }
    if (confirmation_list.includes(code)) {
        confirmation_list.splice(0, confirmation_list.length);
        return true;
    }
    else
        return false;
}
