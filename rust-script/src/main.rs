use ktu_pdf2xl::{parse::parse_pdf};
use std::time::Instant;

fn main() {
    let start_time = Instant::now(); //time_benchmark

    println!(" --------------------- ");
    println!(" ---- ktu_pdf2xl ----- ");
    println!(" --------------------- ");
    println!("INFO: starting conversion");


    let pdf_data = parse_pdf("Samples/VASResult1.pdf");
    println!("{pdf_data}");

    let duration = start_time.elapsed(); //time_benchmark
    println!("Time taken: {:?}", duration); //time_benchmark
}


