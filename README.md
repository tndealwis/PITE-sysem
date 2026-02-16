# PITE: Personal Income Tax Exemption System

PITE is a distributed tax calculation system built with **Python**, **Pyro4**, and **SQLite**. It serves as a robust backend for managing taxpayer information, processing payroll records, and calculating various tax obligations including taxable income, tax withheld, Medicare levies, and surcharges.

The system leverages **Remote Procedure Calls (RPC)** to separate the client interface from the core tax calculation logic, ensuring scalability and maintainability.

## Features

- **Distributed Architecture**: Client-Server communication via Pyro4 RPC.
- **Taxpayer Verification**: Validates Tax File Numbers (TFN) against a secure database.
- **Comprehensive Tax Calculations**:
  - Taxable Income & Net Income calculation.
  - Tax Withholding estimation.
  - Australian Tax Bracket application.
  - Medical Levy & Medicare Levy Surcharge (MLS) calculations.
- **Data Persistence**: Uses SQLite for reliable storage of taxpayer and payroll data.

## Prerequisites

Ensure you have the following installed:

- **Python 3.x**
- **pip** (Python Package Installer)
- **SQLite3** markdown (usually pre-installed with Python or OS)

## Installation & Setup

Follow these steps to set up the project environment.

### 1. Clone the Repository

```bash
git clone https://github.com/tndealwis/PITE-sysem.git
```

### 2. Initialize the Database

Create the database schema and populate initial data:

```bash
sqlite3 tax.db < create_sql.sql
```

### 3. Set Up Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

---

## Usage

The system requires three separate terminal instances to run the Name Server, the Tax Server, and the Client.

**Note:** Ensure the virtual environment is activated in **all** terminals before running commands.

### Terminal 1: Start the Name Server

The Pyro4 Name Server manages object registration. Keep this terminal running.

```bash
python -m Pyro4.naming
```

> **Note:** Do not close this terminal while the system is in use.

### Terminal 2: Start the Tax Server

The server handles logic and database interactions.

```bash
python server.py
```

### Terminal 3: Run the Client

The client interface for interacting with the system.

```bash
python client.py
```
