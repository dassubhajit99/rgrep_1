use colored::Colorize;
use std::env;
use std::fs;
use std::io::BufRead;
use std::io::BufReader;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        panic!("3 arguments is required")
    }
    let query_text = &args[1];
    let filename = &args[2];

    // let contents = fs::read_to_string(filename).expect("File read error");

    // for line in contents.lines() {
    //     println!("{line}")
    // }

    let file = fs::File::open(filename)?;

    let reader = BufReader::new(file);

    println!("{:?}", reader);

    for line in reader.lines() {
        match line {
            Ok(s) => {
                if s.contains(query_text) {
                    println!(
                        "{}",
                        s.replace(query_text, &query_text.red().bold().to_string())
                    )
                }
            }
            Err(e) => println!("Something went wrong while reading line {e}"),
        }
    }

    Ok(())
}
