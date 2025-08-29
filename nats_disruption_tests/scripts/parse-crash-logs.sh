#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


# Script to parse crash logs and identify the source file under site-packages/univention/provisioning
# Usage: ./parse-crash-logs.sh [logfile]

set -euo pipefail

# Colors for output
RED=""
GREEN=""
YELLOW=""
BLUE=""
NC=""
# RED='\033[0;31m'
# GREEN='\033[0;32m'
# YELLOW='\033[1;33m'
# BLUE='\033[0;34m'
# NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 [logfile]"
    echo "If no logfile is provided, will search for *.crash.*.log files in current directory"
    echo ""
    echo "Examples:"
    echo "  $0 udm-transformer.crash.20250827-02071756253235.log"
    echo "  $0  # Will analyze the most recent crash log"
}

analyze_log() {
    local logfile="$1"
    echo -e "${BLUE}Analyzing crash log: ${logfile}${NC}"
    echo "==========================================="

    # Find the last traceback/exception in the log
    local last_traceback_line=""
    if grep -q "Traceback\|Exception Group Traceback" "$logfile"; then
        last_traceback_line=$(grep -n "Traceback\|Exception Group Traceback" "$logfile" | tail -1 | cut -d: -f1 || true)
    fi

    if [[ -z "$last_traceback_line" ]]; then
        echo -e "${YELLOW}No traceback found in log file${NC}"
        return 1
    fi

    echo -e "${GREEN}Last error found at line ${last_traceback_line}${NC}"
    echo ""

    # Extract the traceback section (from last traceback to end of file or next non-traceback line)
    local traceback_end=""
    local total_lines
    total_lines=$(wc -l < "$logfile")

    # Look for the end of the exception block - either next log entry or end of file
    traceback_end=$(tail -n +$((last_traceback_line + 1)) "$logfile" | grep -n "^[^[:space:]].*|.*INFO\|^[^[:space:]].*|.*DEBUG\|^[^[:space:]].*|.*WARNING\|^[^[:space:]].*+----" | head -1 | cut -d: -f1 || true)

    if [[ -z "$traceback_end" ]]; then
        # If no clear end found, take rest of file (this handles cases where log ends with error)
        actual_end=$total_lines
    else
        actual_end=$((last_traceback_line + traceback_end - 1))
    fi

    echo -e "${YELLOW}=== FULL TRACEBACK ===${NC}"
    sed -n "${last_traceback_line},${actual_end}p" "$logfile"
    echo ""

    # Find files under site-packages/univention/provisioning in the traceback
    echo -e "${YELLOW}=== UNIVENTION PROVISIONING FILES INVOLVED ===${NC}"

    local found_files=()
    local line_numbers=()

    # Use grep to find univention provisioning files and extract info
    while IFS= read -r line; do
        if echo "$line" | grep -q "site-packages/univention/provisioning"; then
            # Extract file path after site-packages/univention/provisioning/
            local file_path
            file_path=$(echo "$line" | sed 's/.*site-packages\/univention\/provisioning\/\([^"]*\)".*/\1/')
            found_files+=("$file_path")

            # Try to extract line number from the same line
            if echo "$line" | grep -q "line [0-9]"; then
                local line_num
                line_num=$(echo "$line" | sed 's/.*line \([0-9]*\).*/\1/')
                line_numbers+=("$line_num")
            else
                line_numbers+=("")
            fi
        fi
    done < <(sed -n "${last_traceback_line},\$p" "$logfile")

    if [[ ${#found_files[@]} -eq 0 ]]; then
        echo -e "${RED}No files under site-packages/univention/provisioning found in traceback${NC}"
        return 1
    fi

    # Show files with line numbers
    for i in "${!found_files[@]}"; do
        local file="${found_files[$i]}"
        local line_num="${line_numbers[$i]}"

        echo -ne "${GREEN}📁 ${file}${NC}"
        if [[ -n "$line_num" ]]; then
            echo -e "   ${BLUE}Line: ${line_num}${NC}"
        fi
    done

    echo ""

    # Find the last "raise" statement in the file
    local raise_line_num=""
    if grep -q "raise" "$logfile"; then
        raise_line_num=$(grep -n "raise" "$logfile" | tail -1 | cut -d: -f1 || true)
    fi

    if [[ -n "$raise_line_num" ]]; then
        # Get the line right after the raise statement
        local error_line
        error_line=$(sed -n "$((raise_line_num + 1))p" "$logfile" || true)

        if [[ -n "$error_line" ]]; then
            # Extract everything after the last "|"
            local clean_error
            clean_error=$(echo "$error_line" | sed 's/^.*|[[:space:]]*//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
            echo -e "ERROR DETAILS ${RED}💥 ${clean_error}${NC}"
        else
            echo -e "${YELLOW}No error line found after raise statement${NC}"
        fi
    else
        echo -e "${YELLOW}No raise statement found in log${NC}"
    fi

    # Show the root cause (last file in our codebase)
    echo ""
    if [[ ${#found_files[@]} -gt 0 ]]; then
        local root_cause_file="${found_files[-1]}"
        echo -ne "ROOT CAUSE ${RED}🔥 Primary issue in: ${root_cause_file}${NC}"
        if [[ -n "${line_numbers[-1]}" ]]; then
            echo -e "${RED}   At line: ${line_numbers[-1]}${NC}"
        fi
    else
        echo -e "${YELLOW}Could not determine root cause file${NC}"
    fi

    return 0
}

main() {
    local logfile=""

    if [[ $# -eq 0 ]]; then
        # Find the most recent crash log
        logfile=$(find . -name "*.crash.*.log" -type f -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)

        if [[ -z "$logfile" ]]; then
            echo -e "${RED}No crash log files found in current directory${NC}"
            print_usage
            exit 1
        fi

        echo -e "${BLUE}Auto-selected most recent crash log: ${logfile}${NC}"
        echo ""
    elif [[ $# -eq 1 ]]; then
        logfile="$1"

        if [[ "$logfile" == "-h" ]] || [[ "$logfile" == "--help" ]]; then
            print_usage
            exit 0
        fi

        if [[ ! -f "$logfile" ]]; then
            echo -e "${RED}Error: Log file '$logfile' not found${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Error: Too many arguments${NC}"
        print_usage
        exit 1
    fi

    analyze_log "$logfile"
}

main "$@"
