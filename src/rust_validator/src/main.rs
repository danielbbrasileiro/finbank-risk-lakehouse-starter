use anyhow::{anyhow, Result};
use clap::{Parser, Subcommand};
use serde::Deserialize;
use std::collections::{HashMap, HashSet};
use std::fs;

#[derive(Parser)]
#[command(name = "finbank-validator")]
#[command(about = "Fast CSV schema validator for the FinBank Risk Lakehouse project")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Validate {
        #[arg(long)]
        input: String,

        #[arg(long)]
        schema: String,
    },
}

#[derive(Debug, Deserialize)]
struct Schema {
    name: String,
    required_columns: Vec<String>,
    not_null: Vec<String>,
    unique: Vec<String>,
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Validate { input, schema } => validate_csv(&input, &schema),
    }
}

fn validate_csv(input_path: &str, schema_path: &str) -> Result<()> {
    let schema_text = fs::read_to_string(schema_path)?;
    let schema: Schema = serde_json::from_str(&schema_text)?;

    let mut reader = csv::Reader::from_path(input_path)?;
    let headers = reader.headers()?.clone();

    let header_set: HashSet<String> = headers.iter().map(|s| s.to_string()).collect();

    let mut errors: Vec<String> = Vec::new();

    for col in &schema.required_columns {
        if !header_set.contains(col) {
            errors.push(format!("Missing required column: {}", col));
        }
    }

    let mut unique_trackers: HashMap<String, HashSet<String>> = HashMap::new();
    for col in &schema.unique {
        unique_trackers.insert(col.clone(), HashSet::new());
    }

    let mut row_count = 0usize;

    for result in reader.deserialize::<HashMap<String, String>>() {
        let row = result?;
        row_count += 1;

        for col in &schema.not_null {
            let value = row.get(col).map(|v| v.trim()).unwrap_or("");
            if value.is_empty() {
                errors.push(format!("Row {}: null/empty value in '{}'", row_count, col));
            }
        }

        for col in &schema.unique {
            if let Some(value) = row.get(col) {
                if let Some(seen) = unique_trackers.get_mut(col) {
                    if seen.contains(value) {
                        errors.push(format!("Row {}: duplicate value '{}' in '{}'", row_count, value, col));
                    } else {
                        seen.insert(value.clone());
                    }
                }
            }
        }
    }

    if errors.is_empty() {
        println!("Validation passed for '{}'. Rows checked: {}", schema.name, row_count);
        Ok(())
    } else {
        eprintln!("Validation failed for '{}'. Errors: {}", schema.name, errors.len());
        for err in errors.iter().take(50) {
            eprintln!("- {}", err);
        }
        if errors.len() > 50 {
            eprintln!("... and {} more errors", errors.len() - 50);
        }
        Err(anyhow!("CSV validation failed"))
    }
}
