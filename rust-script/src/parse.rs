use pdfplumber::{Pdf, TextOptions};
use std::{path::Path};
use crate::{PdfDataBuilder};




// fist callable functions
pub fn parse_pdf(file_path: impl AsRef<Path>) -> String { //temporary output of String. Desired
                                                          //output is PdfData

    let mut pdf_data_builder = PdfDataBuilder::default();

    pdf_data_builder.set_pdf_path(file_path.as_ref());

    let pdf = Pdf::open_file(pdf_data_builder.pdf_path(), None).unwrap();
    let pdf_text = extract_text(&pdf);

    //personalNote: remember here RUST checking if the pattern on left is same as right, then assign unboxed valued
    //from right variable to left varible (right variable is old one)
    if let Some(pdf_text) = pdf_text {
        pdf_text
    } else {
        String::from("Failed")
    }

}

// extract the full raw text from every page of pdf
fn extract_text(pdf: &Pdf) -> Option<String> {
    let mut page_number: usize = 0;
    let mut extracted_text = String::new();

    //complete page iterated and extracted
    for single_page in pdf.pages_iter() {
        let page = single_page.unwrap();
        page_number = page.page_number();

        let text = page.extract_text(&TextOptions::default());
        // let text = page.extract_text(&TextOptions {layout: true, ..Default::default() });

        extracted_text.push_str(&text);
    }

    if extracted_text.is_empty() {
        println!("WARN: extracted text empty");
        None
    } else {
        println!("INFO: extracted text from {page_number} pages");
        Some(extracted_text)
    }
}
