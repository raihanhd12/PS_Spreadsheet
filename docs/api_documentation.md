# Google Sheets to DB Sync API Documentation

## Overview

This API allows you to synchronize data between Google Sheets and databases. It provides functionality to connect to
Google Sheets, retrieve data, and sync it to a database either manually or automatically at specified intervals.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses API key authentication. Include the API key in the `X-API-Key` header for all requests.

Example:

```
X-API-Key: your-secure-api-key
```

## Endpoints

### Root Endpoint

```
GET /
```

Returns a simple message confirming the API is running.

**Response:**

```json
{
  "message": "Google Sheets to DB Sync API",
  "version": "1.0.0",
  "status": "running"
}
```

### Health Check

```
GET /health
```

Returns the health status of the API.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2023-03-01T12:00:00.000Z",
  "scheduler": "running",
  "last_sync": "2023-03-01T11:55:00.000Z"
}
```

### Connect to Google Sheets

```
POST /connect-gsheets/
```

Connects to a Google Spreadsheet and returns its data.

**Request Body:**

```json
{
  "spreadsheet_id": "1ABCdefGHIjklMNOpqrSTUvwXYZ12345",
  "credentials": {
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "your-private-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\nYourPrivateKey\n-----END PRIVATE KEY-----\n",
    "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
  },
  "sheet_name": "Sheet1"
}
```

**Response:**

```json
{
  "status": "success",
  "rows": 10,
  "columns": [
    "ID",
    "Name",
    "Email",
    "Phone"
  ],
  "data": [
    {
      "ID": "1",
      "Name": "John Doe",
      "Email": "john@example.com",
      "Phone": "555-1234"
    },
    {
      "ID": "2",
      "Name": "Jane Smith",
      "Email": "jane@example.com",
      "Phone": "555-5678"
    }
    // ... remaining rows
  ]
}
```

### Sync to Database

```
POST /sync-db/
```

Syncs data from a Google Spreadsheet to a database.

**Request Body:**

```json
{
  "spreadsheet_id": "1ABCdefGHIjklMNOpqrSTUvwXYZ12345",
  "credentials": {
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "your-private-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\nYourPrivateKey\n-----END PRIVATE KEY-----\n",
    "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
  },
  "db_config": {
    "db_type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "your_password",
    "database": "your_database",
    "table_name": "your_table"
  },
  "sheet_name": "Sheet1"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Data synced to your_database.your_table",
  "rows_synced": 10
}
```

### Start Auto-Sync

```
POST /start-auto-sync/
```

Starts an automatic synchronization process with a specified interval.

**Request Body:**

```json
{
  "spreadsheet_id": "1ABCdefGHIjklMNOpqrSTUvwXYZ12345",
  "credentials": {
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "your-private-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\nYourPrivateKey\n-----END PRIVATE KEY-----\n",
    "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
  },
  "db_config": {
    "db_type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "your_password",
    "database": "your_database",
    "table_name": "your_table"
  },
  "interval_minutes": 10,
  "sheet_name": "Sheet1"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Auto-sync started every 10 minutes",
  "first_sync": {
    "status": "completed",
    "last_run": "2023-03-01T12:00:00.000Z",
    "rows_synced": 10,
    "error": null
  }
}
```

### Stop Auto-Sync

```
POST /stop-auto-sync/
```

Stops the automatic synchronization process.

**Response:**

```json
{
  "status": "success",
  "message": "Auto-sync stopped"
}
```

### Get Sync Status

```
GET /sync-status
```

Gets the current status of the auto-sync process.

**Response:**

```json
{
  "scheduler": "running",
  "sync": {
    "status": "completed",
    "last_run": "2023-03-01T12:00:00.000Z",
    "rows_synced": 10,
    "error": null
  }
}
```

## Supported Database Types

- `postgresql`
- `mysql`
- `sqlite`
- `mssql`
- Other database types supported by SQLAlchemy

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `200 OK`: The request was successful
- `401 Unauthorized`: Invalid or missing API key
- `409 Conflict`: Resource conflict (e.g., auto-sync already running)
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: An unexpected error occurred
- `502 Bad Gateway`: External service connection error

Error response format:

```json
{
  "status": "error",
  "message": "Error message",
  "detail": "Detailed error information",
  "timestamp": "2023-03-01T12:00:00.000Z"
}
```

## Rate Limiting

The API includes rate limiting to prevent abuse. By default, endpoints are limited to 10 requests per minute.

When the rate limit is exceeded, the API returns:

```json
{
  "detail": "Rate limit exceeded: 10 per 1 minute"
}
```

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

## Environment Variables

The API can be configured using environment variables:

- `DEBUG`: Enable debug mode (true/false)
- `API_KEY`: API key for authentication
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS
- `RATE_LIMIT_PER_MINUTE`: Number of requests allowed per minute
- `DEFAULT_SHEET_NAME`: Default sheet name if not specified in requests
- `DEFAULT_SYNC_INTERVAL`: Default sync interval in minutes
- `MAX_SYNC_INTERVAL`: Maximum allowed sync interval in minutes

See `.env.example` for a template.