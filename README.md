# Google Sheets to DB Sync API

A FastAPI-based API for synchronizing data between Google Sheets and databases.

## Features

- Connect to Google Sheets and retrieve data
- Sync data to a database (PostgreSQL, MySQL, SQLite, etc.)
- Automatically sync data at specified intervals
- Secure API with API key authentication
- Rate limiting to prevent abuse
- Structured logging for better monitoring
- Prometheus metrics for performance tracking

## Project Structure

```
google_sheets_db_sync/
│
├── app/
│   ├── __init__.py
│   ├── api.py             # FastAPI application and endpoints
│   ├── config.py          # Configuration and settings
│   ├── models.py          # Pydantic models
│   ├── exceptions.py      # Custom exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── google_sheets.py  # Google Sheets service
│   │   ├── database.py       # Database service
│   │   └── scheduler.py      # Scheduler service
│   ├── middlewares/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication middleware
│   │   └── rate_limit.py     # Rate limiting middleware
│   └── utils/
│       ├── __init__.py
│       └── logging.py        # Logging setup
│
├── docs/
│   └── api_documentation.md  # API documentation
│
├── .env                      # Environment variables (do not commit)
├── .env.example              # Example environment variables
├── requirements.txt          # Project dependencies
├── main.py                   # Entry point to run the application
└── README.md                 # Project overview
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/google-sheets-db-sync.git
cd google-sheets-db-sync
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

5. Configure your environment variables in the `.env` file.

## Running the API

```bash
python main.py
```

This will start the API server at http://localhost:8000.

## API Documentation

When running in debug mode, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

For detailed API documentation, see [docs/api_documentation.md](docs/api_documentation.md).

## Setting Up Google Service Account

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create a service account:
    - Navigate to "IAM & Admin" > "Service Accounts"
    - Click "Create Service Account"
    - Fill in the details and create the account
    - Create a key for the service account (JSON format)
    - Download the JSON key file
5. Share your Google Spreadsheet with the service account email address (give it Editor access)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.