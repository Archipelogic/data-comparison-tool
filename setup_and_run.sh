#!/bin/bash

# DataFrame Comparison Tool - Setup and Run Script
# This script sets up the environment and runs the analysis

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Banner
echo ""
echo "================================================"
echo "   DataFrame Comparison Tool Setup & Run"
echo "================================================"
echo ""

# Check Python installation
print_status "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PIP_CMD=pip3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    PIP_CMD=pip
else
    print_error "Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Check if we're in the correct directory
if [ ! -f "run_analysis.py" ]; then
    print_error "Please run this script from the data-comparison-tool directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating virtual environment..."
    $PYTHON_CMD -m venv $VENV_DIR
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
print_status "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data
mkdir -p output
print_success "Directories created"

# Parse command line arguments
DEMO_MODE=false
ROWS=1000
COLS=10
SAVE_DEMO=false
NO_BROWSER=false
DATA_DIR=""
FILES=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --demo)
            DEMO_MODE=true
            shift
            ;;
        --rows)
            ROWS="$2"
            shift 2
            ;;
        --cols)
            COLS="$2"
            shift 2
            ;;
        --save-demo)
            SAVE_DEMO=true
            shift
            ;;
        --no-browser)
            NO_BROWSER=true
            shift
            ;;
        --dir)
            DATA_DIR="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS] [FILES...]"
            echo ""
            echo "Options:"
            echo "  --demo           Use synthetic demo data"
            echo "  --rows N         Number of rows for demo data (default: 1000)"
            echo "  --cols N         Number of columns for demo data (default: 10)"
            echo "  --save-demo      Save demo datasets to data folder"
            echo "  --no-browser     Do not open report in browser"
            echo "  --dir PATH       Load all files from directory"
            echo "  --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --demo                    # Run with demo data"
            echo "  $0 --demo --rows 5000        # Larger demo dataset"
            echo "  $0 --dir data/               # Load from data directory"
            echo "  $0 file1.csv file2.json      # Compare specific files"
            exit 0
            ;;
        *)
            FILES="$FILES $1"
            shift
            ;;
    esac
done

# Build command
CMD="python run_analysis.py"

if [ "$DEMO_MODE" = true ]; then
    CMD="$CMD --demo --rows $ROWS --cols $COLS"
    if [ "$SAVE_DEMO" = true ]; then
        CMD="$CMD --save-demo"
    fi
elif [ -n "$DATA_DIR" ]; then
    CMD="$CMD --dir $DATA_DIR"
elif [ -n "$FILES" ]; then
    CMD="$CMD $FILES"
else
    # Default to demo mode if no input specified
    print_warning "No input specified, using demo mode"
    CMD="$CMD --demo"
fi

if [ "$NO_BROWSER" = true ]; then
    CMD="$CMD --no-browser"
fi

# Run analysis
echo ""
print_status "Running analysis..."
echo "Command: $CMD"
echo ""
echo "================================================"
eval $CMD
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    print_success "Setup and analysis completed successfully!"
    echo ""
    echo "To run the analysis again, you can use:"
    echo "  ./setup_and_run.sh --demo"
    echo "  ./setup_and_run.sh --dir data/"
    echo "  python run_analysis.py --help  (for more options)"
    echo ""
else
    print_error "Analysis failed with exit code $EXIT_CODE"
    exit $EXIT_CODE
fi
