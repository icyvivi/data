# Financial Market Data Collector

A collection of Python scripts for fetching, processing, and storing financial market data from various sources.

## Overview

This project provides tools to collect financial market data from different exchanges and APIs. The data is stored in CSV format for further analysis and processing.

## Features

- Fetch Singapore market data from SGX API
- Fetch Hong Kong market data
- Fetch US market data (Finviz)
- Automatic data directory management
- Timestamped logging

## Project Structure

```
data/
├── collector/
│   ├── sg_spot.py     # Singapore market data collector
│   ├── hk.py          # Hong Kong market data collector
│   └── finviz.py      # US market data collector (Finviz)
├── data/              # Data storage directory
│   ├── sg_tickers_spot.csv
│   ├── hk_tickers_info.csv
│   └── us_tickers_overview.csv
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Installation

1. Clone this repository
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Singapore Market Data

To collect Singapore market data:

```bash
python collector/sg_spot.py
```

This will fetch the latest data from SGX API and save it to `data/sg_tickers_spot.csv`.

### Hong Kong Market Data

To collect Hong Kong market data:

```bash
python collector/hk.py
```

### US Market Data (Finviz)

To collect US market data from Finviz:

```bash
python collector/finviz.py
```

## Data Format

### Singapore Market Data (sg_tickers_spot.csv)

The Singapore market data includes the following fields:
- Stock ticker symbols
- Price information (open, high, low, close)
- Volume data
- Change vs previous close
- Timestamp information

## Requirements

- Python 3.6+
- pandas
- numpy
- requests
- pytz

## License

See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.