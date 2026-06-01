# ktu_pdf2xl in RUST 
## This is an attempt to create a rewrite of ktupdf2xl backend python script in RUST

### Architecture
the core idea is to provide three public functions that can be imported and called from `lib.rs`
- `parse()` -> extract data from the pdf
- `anlyse()` -> perform analysis on pdf data
- `render()` -> render analysis and pdf data to excel






