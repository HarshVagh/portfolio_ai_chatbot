import * as pdfjsLib from 'pdfjs-dist';

async function extractTextFromPdf(fileBuffer) {
    try {
        // Convert the Buffer to a Uint8Array
        const uint8Array = new Uint8Array(fileBuffer);

        // Load the PDF document
        const pdf = await pdfjsLib.getDocument({ data: uint8Array }).promise;
        let extractedText = '';

        // Extract text from each page
        for (let i = 0; i < pdf.numPages; i++) {
            const page = await pdf.getPage(i + 1);
            const textContent = await page.getTextContent();
            const pageText = textContent.items.map(item => item.str).join(' ');
            extractedText += pageText + '\n';
        }

        return extractedText.trim();
    } catch (error) {
        console.error(`Error extracting text from PDF: ${error.message}`);
        return '';
    }
}

export default extractTextFromPdf;
