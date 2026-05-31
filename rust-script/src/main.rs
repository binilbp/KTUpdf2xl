use ktu_pdf2xl::convert_pdf;
use std::time::Instant;

fn main() {
    let start_time = Instant::now(); //time_benchmark

    // getting the file from Samples folder with name VASResult1.pdf"
    let pdf_text = convert_pdf("Samples/VASResult1.pdf");
    println!("{pdf_text}");

    let duration = start_time.elapsed(); //time_benchmark
    println!("Time taken: {:?}", duration); //time_benchmark
}
