#!/bin/bash

# Ordinal Frame - GitHub Repository Setup
# Run this script from your cloned GitHub repository directory

set -e  # Exit on any error

echo "🖼️  Ordinal Frame - GitHub Repository Setup"
echo "============================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a git repository
check_git_repo() {
    if [ ! -d ".git" ]; then
        log_error "Not in a git repository. Please run this from your cloned repo directory."
        echo "Run: git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git"
        echo "Then: cd YOUR-REPO-NAME"
        echo "Then: ./setup-repo.sh"
        exit 1
    fi
    
    log_success "Git repository detected"
    
    # Show repo info
    REPO_URL=$(git remote get-url origin 2>/dev/null || echo "No remote origin")
    BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
    log_info "Repository: $REPO_URL"
    log_info "Current branch: $BRANCH"
}

# Check system requirements
check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check if on macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_warning "This script is optimized for macOS"
    fi
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install:"
        echo "  brew install python@3.11"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_info "Installing pip..."
        python3 -m ensurepip --upgrade
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        log_error "Git not found. Please install Xcode command line tools:"
        echo "  xcode-select --install"
        exit 1
    fi
    
    log_success "System requirements satisfied"
    log_info "Python: $(python3 --version)"
    log_info "Git: $(git --version)"
}

# Create project structure
create_project_structure() {
    log_info "Creating project structure..."
    
    # Create directories
    mkdir -p {templates,static/{css,js,images},ordinals/{cached,metadata},logs,tests,docs}
    
    # Create placeholder files
    touch logs/.gitkeep
    touch ordinals/cached/.gitkeep
    touch ordinals/metadata/.gitkeep
    touch tests/.gitkeep
    touch static/css/.gitkeep
    touch static/js/.gitkeep
    touch static/images/.gitkeep
    
    log_success "Project structure created"
}

# Create Python virtual environment
setup_virtual_environment() {
    log_info "Setting up Python virtual environment..."
    
    # Remove existing venv if it exists
    if [ -d "venv" ]; then
        log_warning "Removing existing virtual environment..."
        rm -rf venv
    fi
    
    # Create new virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip and essential tools
    pip install --upgrade pip setuptools wheel
    
    log_success "Virtual environment created and activated"
}

# Create requirements.txt
create_requirements() {
    log_info "Creating requirements.txt..."
    
    cat > requirements.txt << 'EOF'
# Ordinal Frame Dependencies

# Web Framework
Flask==3.0.0
Werkzeug==3.0.1

# HTTP Requests & APIs
requests==2.31.0
urllib3==2.1.0

# Image Processing
Pillow==10.1.0

# Bitcoin Libraries
bitcoinlib==0.12.0
ecdsa==0.18.0

# Data Processing
pandas==2.1.4
numpy==1.25.2

# JSON & Validation
jsonschema==4.20.0
marshmallow==3.20.2

# Caching & Storage
diskcache==5.6.3

# Date & Time Utilities
python-dateutil==2.8.2

# Development & Testing
pytest==7.4.3
pytest-flask==1.3.0
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
mypy==1.7.1

# Production Server
gunicorn==21.2.0

# System Monitoring
psutil==5.9.6

# Enhanced Logging
coloredlogs==15.0.1

# Environment Management
python-dotenv==1.0.0
EOF
    
    log_success "requirements.txt created"
}

# Install dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Make sure we're in the virtual environment
    source venv/bin/activate
    
    # Install all requirements
    pip install -r requirements.txt
    
    log_success "Dependencies installed successfully"
}

# Create environment configuration
create_environment_config() {
    log_info "Creating environment configuration..."
    
    # Create .env file for development
    cat > .env << 'EOF'
# Ordinal Frame Configuration

# Flask Settings
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Server Settings
HOST=0.0.0.0
PORT=5000

# API Settings
HIRO_API_BASE_URL=https://api.hiro.so/ordinals/v1
REQUEST_TIMEOUT=30
MAX_RETRIES=3

# Cache Settings
CACHE_DIR=ordinals/cached
METADATA_FILE=ordinals/metadata/ordinals.json
SELECTION_FILE=ordinals/metadata/selection.json

# Image Settings
MAX_IMAGE_SIZE_MB=50
SUPPORTED_FORMATS=jpg,jpeg,png,gif,svg,webp,avif

# Display Settings
DEFAULT_SLIDESHOW_INTERVAL=30
TOUCH_HOLD_DURATION=500

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/ordinal-frame.log
EOF
    
    # Create .env.example for sharing
    cp .env .env.example
    sed -i '' 's/SECRET_KEY=.*/SECRET_KEY=your-secret-key-here/' .env.example
    
    log_success "Environment configuration created"
}

# Create .gitignore
create_gitignore() {
    log_info "Creating .gitignore..."
    
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
.venv/
ENV/
env/
.env.local
.env.production

# IDE & Editors
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# Logs
*.log
logs/*.log
!logs/.gitkeep

# Cache & Temporary Files
.cache/
*.tmp
*.temp
.pytest_cache/
.coverage
htmlcov/

# Ordinal Frame Specific
ordinals/cached/*
!ordinals/cached/.gitkeep
ordinals/metadata/ordinals.json
ordinals/metadata/selection.json

# Environment Variables
.env
!.env.example

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Raspberry Pi deployment
*.img
*.zip
deployment/

# Documentation builds
docs/_build/
EOF
    
    log_success ".gitignore created"
}

# Create development tools
create_dev_tools() {
    log_info "Creating development tools..."
    
    # Makefile for common tasks
    cat > Makefile << 'EOF'
.PHONY: help install dev test lint format run clean setup

help: ## Show this help message
	@echo "Ordinal Frame Development Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Initial project setup
	python3 -m venv venv
	source venv/bin/activate && pip install --upgrade pip setuptools wheel
	source venv/bin/activate && pip install -r requirements.txt

install: ## Install dependencies
	source venv/bin/activate && pip install -r requirements.txt

dev: ## Install in development mode
	source venv/bin/activate && pip install -e .

test: ## Run tests
	source venv/bin/activate && pytest tests/ -v

test-cov: ## Run tests with coverage
	source venv/bin/activate && pytest tests/ --cov=. --cov-report=html

lint: ## Run linting
	source venv/bin/activate && flake8 *.py
	source venv/bin/activate && black --check *.py
	source venv/bin/activate && mypy *.py

format: ## Format code
	source venv/bin/activate && black *.py

run: ## Run development server
	source venv/bin/activate && python server.py

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/

deploy-pi: ## Deploy to Raspberry Pi (requires PI_HOST env var)
	@if [ -z "$(PI_HOST)" ]; then echo "Set PI_HOST environment variable"; exit 1; fi
	rsync -av --exclude='.git' --exclude='venv' --exclude='__pycache__' . pi@$(PI_HOST):~/ordinal-frame/
	ssh pi@$(PI_HOST) "cd ordinal-frame && ./setup-pi.sh"
EOF
    
    # pytest configuration
    cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --strict-config
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
EOF
    
    # Black configuration
    cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | build
  | dist
)/
'''

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
EOF
    
    log_success "Development tools created"
}

# Create README.md
create_readme() {
    log_info "Creating README.md..."
    
    cat > README.md << 'EOF'
# 🖼️ Ordinal Frame

A Bitcoin-native digital art display that verifies ownership and displays your Ordinals collection on a Raspberry Pi touchscreen.

![Ordinal Frame Demo](static/images/demo.gif)

## Why This Exists

Unlike NFTs that rely on off-chain metadata, Bitcoin Ordinals are inscribed directly on-chain, making them permanent and truly decentralized. This frame celebrates that permanence by providing a dedicated display for your collection.

## Features

- ✅ **Wallet Integration** - Enter your Bitcoin address to fetch your Ordinals
- ✅ **Collection Selection** - Pick and choose which pieces to display  
- ✅ **Touch Interface** - Tap to cycle, long-press for metadata
- ✅ **Offline Operation** - Works without internet after setup
- ✅ **Auto-slideshow** - Cycles through your collection automatically
- ✅ **Kiosk Mode** - Boots directly to fullscreen display

## Quick Start

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/ordinal-frame.git
   cd ordinal-frame
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup-repo.sh
   ./setup-repo.sh
   ```

3. **Start the development server:**
   ```bash
   make run
   # or manually:
   source venv/bin/activate
   python server.py
   ```

4. **Open your browser:**
   - Setup: http://localhost:5000/setup
   - Frame: http://localhost:5000/frame

### Hardware Requirements (for Pi deployment)

- **Raspberry Pi 5** (8GB RAM recommended)
- **Waveshare 10.1" Capacitive Touchscreen** (1280×800)
- **128GB+ microSD card**
- **Official Pi power supply**

## Development

### Project Structure
```
ordinal-frame/
├── server.py              # Main Flask application
├── templates/             # HTML templates
├── static/               # CSS, JS, assets
├── ordinals/             # Ordinal data and cache
│   ├── cached/          # Downloaded images
│   └── metadata/        # JSON metadata
├── tests/               # Test suite
└── docs/                # Documentation
```

### Available Commands
```bash
make help        # Show all available commands
make run         # Run development server
make test        # Run test suite
make lint        # Check code quality
make format      # Format code with Black
make clean       # Clean up temporary files
```

### API Endpoints

- `GET /` - Landing page
- `GET /setup` - Wallet address setup
- `GET /select` - Ordinal selection interface  
- `GET /frame` - Main display interface
- `POST /api/fetch-ordinals` - Fetch Ordinals for address
- `POST /api/update-selection` - Update display selection
- `GET /api/health` - Health check

## Deployment

### Raspberry Pi

1. **Prepare your Pi:**
   ```bash
   # Flash Raspberry Pi OS to SD card
   # Enable SSH and configure WiFi
   ```

2. **Deploy the application:**
   ```bash
   PI_HOST=192.168.1.100 make deploy-pi
   ```

3. **Configure kiosk mode:**
   ```bash
   ssh pi@your-pi-ip
   cd ordinal-frame
   sudo ./setup-kiosk.sh
   ```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `make test`
5. Format code: `make format`
6. Submit a pull request

## API Integration

Currently supports:
- **Hiro Ordinals API** - Primary data source
- **Ordinals.com API** - Fallback option
- **Bitcoin Core RPC** - For advanced verification (optional)

## Roadmap

- [x] **Phase 1** - Basic wallet integration and display
- [ ] **Phase 2** - Message signing for ownership verification
- [ ] **Phase 3** - Multi-wallet support and collections
- [ ] **Phase 4** - Advanced display modes and customization

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR-USERNAME/ordinal-frame/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR-USERNAME/ordinal-frame/discussions)
- **Documentation**: [docs/](docs/)

---

*Built with ❤️ for the Bitcoin community*
EOF
    
    log_success "README.md created"
}

# Create initial commit
create_initial_commit() {
    log_info "Creating initial commit..."
    
    # Add all files
    git add .
    
    # Check if there are changes to commit
    if git diff --staged --quiet; then
        log_warning "No changes to commit"
        return
    fi
    
    # Create initial commit
    git commit -m "🖼️ Initial Ordinal Frame setup

- Add complete Flask server with Bitcoin API integration
- Add wallet address setup interface
- Add development environment configuration
- Add comprehensive documentation
- Add testing and linting tools"
    
    log_success "Initial commit created"
    
    # Show git status
    log_info "Repository status:"
    git status --short
    git log --oneline -5
}

# Show next steps
show_next_steps() {
    echo ""
    echo "🎉 GitHub repository setup complete!"
    echo ""
    echo "📋 Next Steps:"
    echo ""
    echo "1. **Copy the main application files:**"
    echo "   - Copy server.py from the Flask server artifact"
    echo "   - Copy templates/setup.html from the setup template artifact"
    echo ""
    echo "2. **Test the application:**"
    echo "   source venv/bin/activate"
    echo "   python server.py"
    echo "   # Visit: http://localhost:5000/setup"
    echo ""
    echo "3. **Push to GitHub:**"
    echo "   git push origin main"
    echo ""
    echo "4. **Continue development:**"
    echo "   make help    # See all available commands"
    echo "   make run     # Start development server"
    echo "   make test    # Run tests"
    echo ""
    echo "🛠️  Development workflow:"
    echo "   1. Edit code"
    echo "   2. Run: make test && make lint"
    echo "   3. Commit: git add . && git commit -m 'message'"
    echo "   4. Push: git push"
    echo ""
    echo "📁 Repository: $(pwd)"
    echo "🌐 Ready to build your Ordinal Frame!"
}

# Main execution
main() {
    check_git_repo
    check_system_requirements
    create_project_structure
    setup_virtual_environment
    create_requirements
    install_dependencies
    create_environment_config
    create_gitignore
    create_dev_tools
    create_readme
    create_initial_commit
    show_next_steps
}

# Run the setup
main "$@"