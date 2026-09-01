#!/bin/bash

# TOKEN_RETRIEVER.sh - Extract reMarkable device token from rmapi configuration

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

print_info() {
    echo -e "$1"
}

check_rmapi() {
    if ! command -v rmapi &> /dev/null; then
        print_error "rmapi is not installed or not in PATH"
        print_info ""
        print_info "Install rmapi from: https://github.com/ddvk/rmapi"
        print_info ""
        print_info "On macOS:"
        print_info "  brew install rmapi"
        exit 1
    fi
}

find_config_file() {
    local common_locations=(
        "$HOME/.rmapi"
        "$HOME/.config/rmapi/rmapi.conf"
        "$HOME/.rmapi.conf"
        "$HOME/Library/Application Support/rmapi/rmapi.conf"
        "/etc/rmapi.conf"
        "/usr/local/etc/rmapi.conf"
    )

    for location in "${common_locations[@]}"; do
        if [[ -f "$location" ]]; then
            print_info "Found rmapi config: $location" >&2
            echo "$location"
            return 0
        fi
    done

    if [[ -d "$HOME" ]]; then
        local found_file
        found_file=$(find "$HOME" -name "rmapi.conf" -type f 2>/dev/null | head -1)
        if [[ -n "$found_file" ]]; then
            print_info "Found rmapi config: $found_file" >&2
            echo "$found_file"
            return 0
        fi
    fi

    print_error "No rmapi configuration file found"
    print_info ""
    print_info "Run rmapi once to authenticate, then run this script again:"
    print_info "  rmapi"
    return 1
}

extract_device_token() {
    local config_file="$1"

    if [[ ! -r "$config_file" ]]; then
        print_error "Cannot read config file: $config_file"
        return 1
    fi

    local device_token
    device_token=$(grep "^devicetoken:" "$config_file" 2>/dev/null | cut -d' ' -f2- | tr -d ' ')

    if [[ -z "$device_token" ]]; then
        print_error "No device token found in config file: $config_file"
        print_info ""
        print_info "Re-authenticate with rmapi, then run this script again:"
        print_info "  rmapi"
        return 1
    fi

    echo "$device_token"
}

main() {
    print_info "reMarkable Device Token Retriever"
    print_info "=================================="
    print_info ""

    print_info "Checking for rmapi installation..."
    check_rmapi
    print_success "rmapi is installed"
    print_info ""

    print_info "Looking for rmapi configuration..."
    local config_file
    config_file=$(find_config_file) || exit 1
    print_info ""

    print_info "Extracting device token..."
    local device_token
    device_token=$(extract_device_token "$config_file") || exit 1

    print_success "Device token found!"
    print_info ""
    print_info "Add this value as the GitHub Actions secret DEVICE_TOKEN:"
    print_info "=================================="
    echo "$device_token"
    print_info "=================================="
}

main "$@"
