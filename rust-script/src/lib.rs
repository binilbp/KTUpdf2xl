use pdfplumber::{Pdf, TextOptions};
use std::path::Path;

// pub struct PdfSettings {
//
// }

enum ResultType {
    RegularOnly,
    SupplyOnly,
    RegularAndSupply,
}

struct DepartmentData {
    department_name: String,
    course_names: Vec<String>,
    result: ResultType,
}

struct PdfData {
    exam_centre: String,
    departments: Vec<DepartmentData>,
    pdf_path: Path,
}

// pub fn convert_pdf(pdf_path: impl AsRef<Path>, pdf_settings: PdfSettings) -> String {
pub fn convert_pdf(pdf_path: impl AsRef<Path>) -> String {
    //simple graffiti ;D
    println!(" --------------------- ");
    println!(" ---- ktu_pdf2xl ----- ");
    println!(" --------------------- ");
    println!("INFO: starting conversion");
    let pdf = Pdf::open_file(pdf_path, None).unwrap();
    let pdf_text = extract_raw_text(pdf);

    if let Some(pdf_text) = pdf_text {
        pdf_text
    } else {
        panic!("ERROR: extracted pdf text empty");
    }
}


// extract the full raw text from every page of pdf
fn extract_raw_text(pdf: Pdf) -> Option<String> {
    let mut page_number: usize = 0;
    let mut extracted_text = String::new();

    for result in pdf.pages_iter() {
        let page = result.unwrap();
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
