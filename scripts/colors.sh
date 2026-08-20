RED='\033[0;31m'
RED_BOLD='\033[1;31m'
GREEN='\033[0;32m'
GREEN_BOLD='\033[1;32m'
YELLOW='\033[0;33m'
YELLOW_BOLD='\033[1;33m'
BLUE='\033[0;34m'
BLUE_BOLD='\033[1;34m'
BOLD='\033[1m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
info_bold() { echo -e "${BLUE_BOLD}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
success_bold() { echo -e "${GREEN_BOLD}[OK]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
warning_bold() { echo -e "${YELLOW_BOLD}[WARN]${NC} $1"; }
error() { echo -e "${RED}[error]${NC} $1"; exit 1; }
error_bold() { echo -e "${RED_BOLD}[ERROR]${NC}"; exit 1; }