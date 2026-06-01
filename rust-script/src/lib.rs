pub mod excel;
pub mod parse;

use std::path::{Path, PathBuf};

#[derive(Debug, Default)]
enum ResultType {
    #[default]
    Regular,
    Supply,
    SupplyRegular,
}

#[derive(Default, Debug)]
struct DepartmentData {
    department_name: String,
    course_names: Vec<String>,
    result: ResultType,
}

//same as PdfDataBuilder but without Options enum only to build after collecting all required data through parsing
pub struct PdfData {
    exam_centre: String,
    departments: Vec<DepartmentData>,
    pdf_path: PathBuf,
}

//struct model with Option use this during parsing, finally use .build() method to create PdfData object with complete data
#[derive(Default, Debug)]
pub struct PdfDataBuilder {
    exam_centre: Option<String>,
    departments: Option<Vec<DepartmentData>>,
    pdf_path: Option<PathBuf>,
}

impl PdfDataBuilder {
    pub fn set_pdf_path(&mut self, file_path: &Path) {
        self.pdf_path = Some(file_path.to_path_buf());
    }

    pub fn pdf_path(&self) -> &Path {
        // personNote: remember .as_deref convert PathBuf -> &PathBuf -> &Path and .unwrap to unwrap Option
        self.pdf_path.as_deref().expect("No path set")
    }

    pub fn set_exam_center(&mut self, data: &str) {
        self.exam_centre = Some(String::from(data));
    }

}


