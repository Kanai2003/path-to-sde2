#!/bin/bash
#
# High-performance load test using Apache Bench (ab)
# Tests URL shortener redirect performance with real short codes
#
# Usage:
#   ./scripts/ab_load_test.sh                    # Default: 10K requests, 500 concurrent
#   ./scripts/ab_load_test.sh -n 50000 -c 1000   # Custom: 50K requests, 1000 concurrent
#   ./scripts/ab_load_test.sh --url http://prod.example.com  # Custom base URL

set -e

# =============================================================================
# Configuration
# =============================================================================
BASE_URL="${BASE_URL:-http://localhost:8000}"
REQUESTS="${REQUESTS:-10000}"
CONCURRENCY="${CONCURRENCY:-500}"
TIMEOUT="${TIMEOUT:-30}"
TARGET_RPS=1000

# All short codes from the database
SHORT_CODES=(
    "bYsawo" "SudFGs" "uCYFsM" "0kDSmt" "vu0efz" "zzkPKA" "tR7Vdc" "QHCwaJ"
    "NAJxo2" "cZ0xdj" "JoTuPk" "IbCZ49" "raQ1al" "tqRaMy" "raWftV" "2NJswf"
    "bLgpSQ" "rEdvNN" "PGSUTX" "Z10Wbk" "XYJNqG" "Va1lHf" "aeKbU1" "hnVyPb"
    "cabRmW" "3lPIRm" "8mbi8g" "e9WDmk" "2eQSNb" "k8RzA4" "2VyjZF" "zgq0kY"
    "pR6mWZ" "qTgiK8" "7jlkev" "0Lx8XA" "yRODCi" "Vd3706" "FMdyjq" "BGCrVD"
    "yJq9lf" "bOTp9G" "pq6KPK" "bYk7eZ" "65GuMz" "nSfDZv" "tdW5mf" "3I84E4"
    "KweGAv" "l9uNea" "45LSkx" "Cz8VTb" "tDSFrI" "JQ7vPh" "PbXgnd" "lEbtMj"
    "BOCBcL" "4A0VC5" "p8P3UY" "UXVOVv" "SD4ReO" "4XMnR5" "hnC8XO" "zyzdYp"
    "ajbCEp" "XmXG6Z" "skcmVk" "QhiING" "zBoVow" "NUvA0o" "O8VtPP" "OVwn9W"
    "NdRe6W" "JP5Duj" "j1NGAR" "UgBYqm" "FNEfwG" "atb13Z" "YtDzJf" "X3idKW"
    "EvTxSn" "55HIEu" "EkT17R" "8N70si" "KB99qe" "Cv7e1T" "O8YnB5" "XzlMIU"
    "Qlnbu9" "z47LOt" "7bfybY" "jKRrbN" "d5eZbd" "sGr6Ox" "cIFj2w" "ijWwGv"
    "s4NEXn" "K3PL8L" "x9OJZO" "aTxsK0" "gs8XGy" "SgHjEb" "B0Xfk7" "kyhS8X"
    "610qPG" "bKc7Nx" "uk387v" "2wYvmx" "k3EUVC" "VAVdZc" "QFZg3D" "WWnm39"
    "EIXQBN" "U1WhHz" "KC1GPy" "LUODQQ" "hVeK3k" "3ZqMTu" "PpDyxz" "GoxezY"
    "M6rVn5" "6ERcJF" "cpnnQs" "VyKsCR" "Pm76fY" "qzaF7A" "PA6TlG" "WPIHZ0"
    "Mi7BbD" "6Ha1BF" "GiIzyp" "5JzzoU" "RqJYHw" "xQffNn" "MfnZUd" "Of22iR"
    "6xehOY" "a66owd" "h9u7ui" "SfY8ub" "qA2o9B" "XAC7rz" "dk0KxV" "6DrtAc"
    "memOWC" "G78NFF" "58lVKd" "eHRK3h" "jlTPxu" "1SEanD" "df1h48" "skQwHV"
    "ZeJMYU" "JERaDz" "gWWw7w" "6ToZpz" "7xQAoG" "juymeD" "QtfcM7" "NgkpI6"
    "1Wcfxj" "CIgeet" "JvTnjj" "D5wsm3" "xPghfZ" "C6fVFR" "JXBS8M" "xBiEJm"
    "TxaoZS" "JayWGA" "ixVEXw" "ovsn6E" "F25x4B" "FgRw5H" "cgHdMg" "sD2wVc"
    "xmuEP5" "MlwwIs" "ic9Yyg" "qPATcB" "DNkDYS" "1wBa6W" "N4akJv" "RI3jdZ"
    "FZPpp2" "Lm5hfh" "n7U6D6" "ZOSz78" "e7iYFD" "SNTxmY" "OXnDcd" "bv0baQ"
    "rfJLpX" "6nslKF" "sTomUM" "W8gInV" "6mGQix" "anLvUB" "HUip0c" "Eat6Ak"
    "L7Qn8V" "DsXB26" "8FtFjY" "E1qU0i" "W72lex" "FLttRS" "3kzFit" "QZPoNO"
    "Dcobly" "e4uxD2" "Q6Ol1C" "VZcS6K" "8mKUHW" "fMbkZP" "F9reXB" "hqh4LD"
    "fILpU7" "GT2mLi" "LyLPX4" "WJ7h1B" "WzkDTQ" "1VkacB" "bkaJyv" "PEZIDe"
    "SbMZAx" "d5ikIi" "TU8Fjr" "jc3cJ2" "YYybDI" "VJ5DMV" "0EI8Df" "VPJp60"
    "TvVlkZ" "mmkNGo" "sYl2eZ" "uZo5Nr" "WBPneE" "u1CJt7" "46F2wt" "o5E9l8"
    "wKZb4t" "cp35zD" "65l9su" "WcP9qQ" "WBjdzx" "xU9Xeh" "br6itA" "Zi0a8d"
    "2YWMTt" "dzbZA6" "Ww7N11" "hidlZC" "707gHu" "NSze2v" "vHlULq" "DounBA"
    "t1s7uM" "WIe4nL" "KHgkqx" "QliIYV" "l4JfjM" "iW3Pn1" "gEXA5n" "DQ4lI4"
    "D5SCE6" "GziEP4" "V90wJL" "6q4AG5" "NSum5Q" "C6mZRW" "mYEcnu" "VRYasl"
    "XASSL3" "7JCGlE" "6QdKCP" "l7Y4JQ" "jRdtIe" "jwCqlQ" "W8pygq" "p2HtHQ"
    "6eXY5C" "UTrWy6" "PxxjIt" "zcDo3E" "tuFxrb" "DwJig8" "4bl2Nm" "qv7Zx2"
    "iCzcCx" "5Ee7nb" "eAxumv" "7SabPD" "X5Oe2m" "hyNFB3" "jNa5A6" "h8RcX1"
    "j7sEhe" "GWyVWu" "qmb98z" "BDPmL4" "fATSfI" "ETAFvf" "TN6DF4" "RqaESd"
    "oSDozl" "svXcdU" "z9LrUa" "tdT1ZA" "qwrc8a" "zRoyMy" "tGg4y2" "PplEzk"
    "bXzNRM" "OMfGzM" "dIrxBv" "hBnCyK" "NjHZCk" "1VOGH5" "ZgDqfM" "DnMGKy"
    "Y034Gj" "tB3f9B" "P2N98i" "Q2TO32" "4SKpUo" "p7ostL" "Sl8B3W" "xeMQAe"
    "530FpH" "1qNwGi" "iCl5xa" "U3PNEn" "YkPMXd" "EY9bBq" "l1l1Px" "qffjLJ"
    "aUxNcq" "rOOPZh" "Hfs2gJ" "FXsVQi" "g43xbY" "fRuqgo" "1N6jlO" "saUXjm"
    "qZY5M8" "c6gRgp" "RnZ1rt" "aa5voA" "tgKkSO" "JUt3Tz" "5GVwld" "PXudyK"
    "z3lTed" "1wEuZ7" "jZYId4" "35QoEj" "U1T4A1" "54faqZ" "1ZefKu" "K44eI6"
    "NkFHXX" "iTVQWL" "mUNkOT" "MTAsI8" "ksNlJG" "3wiBk6" "St153Y" "c5ubDV"
    "HAjZyz" "Cs2Lpk" "BgrP0l" "kMqKTk" "X9SNI6" "tfySZw" "m7mdAk" "rGP5JB"
    "ZTFxz9" "JoGAan" "aIYVnC" "IC330m" "Pbma7o" "2yak72" "6VX1H0" "jHkccX"
    "jCti3x" "jsCnu4" "PKYsyV" "ch9FRj" "f1qcKV" "FoJpAI" "SSGxGO" "kRF2cF"
    "3nFr7e" "xH8EYf" "Cf41oy" "gto8Up" "cn648N" "jKIxBq" "J5hW6d" "fqn8fZ"
    "Zdq050" "lShKjq" "67lxOt" "I8vTww" "fOjwda" "sBfNDW" "tXbl97" "SrxCp8"
    "w19FvT" "XVT3kt" "OyDxkf" "P5fwK9" "ntENPY" "1UPnH0" "DaAvYz" "MuFUAe"
    "p1UCtc" "uHS1Q8" "zrCNP6" "LqZo11" "QRpNTk" "rYiljl" "S6kawu" "ulCpem"
    "zSrI0J" "EGqyAU" "QXI8xG" "DGXzT0" "UTnnvh" "jseduc" "hJfMEc" "DLFSsm"
    "HEmrPY" "d1xWT8" "rEMgAU" "lH45mr" "PIKMG3" "ae8rpq" "lgIONH" "HXIG4G"
    "Daww60" "0Su5lL" "2yqFyU" "E3whdH" "bAa9Pi" "egmlQK" "Dkyt3a" "cgCwjZ"
    "VUNOOY" "eokyKL" "oZe7x6" "XkzCXe" "RMlzzJ" "gch0DO" "ERTv2N" "l1qnRJ"
    "mHj7fg" "64skaE" "cJmbir" "CwsNT2" "hWTATy" "ObFsu0" "ddgCUi" "Q3IspF"
    "f3HZbl" "jbcD53" "0xb4F1" "d4FGW2" "d6C36h" "eq8Kng" "tHBEvS" "nhoRm8"
    "qzQLCv" "RURY4B" "Ngm5VO" "2csbJI" "5H8Zf9" "ypEVQj" "eLCa9r" "f7G0CP"
    "sZjOZQ" "bSrscU" "ifDgO1" "Jr80MR" "Q39OdE" "0LwZES" "G3w3mz" "thkoWv"
    "KZBzXb" "RPVEUb" "bYMjVq" "YzHMFG" "5ns85r" "nX5tVn" "hmDHsT" "cUI0kx"
    "igsFeR" "K0jkNF" "dLIXcT" "XsW40J" "QcnVKE" "gu9xdA"
)

# =============================================================================
# Parse arguments
# =============================================================================
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--requests)
            REQUESTS="$2"
            shift 2
            ;;
        -c|--concurrent)
            CONCURRENCY="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --url)
            BASE_URL="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -n, --requests N     Total number of requests (default: 10000)"
            echo "  -c, --concurrent N   Number of concurrent connections (default: 500)"
            echo "  -t, --timeout N      Socket timeout in seconds (default: 30)"
            echo "  --url URL            Base URL (default: http://localhost:8000)"
            echo "  -h, --help           Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                           # Default test"
            echo "  $0 -n 50000 -c 1000          # Heavy load test"
            echo "  $0 --url http://prod:8000    # Test production"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# =============================================================================
# Check dependencies
# =============================================================================
if ! command -v ab &> /dev/null; then
    echo "❌ Apache Bench (ab) not found. Install with:"
    echo "   sudo apt-get install apache2-utils"
    exit 1
fi

# =============================================================================
# Print header
# =============================================================================
NUM_CODES=${#SHORT_CODES[@]}

echo ""
echo "============================================================"
echo "  URL SHORTENER LOAD TEST (Apache Bench)"
echo "============================================================"
echo "  Base URL:     $BASE_URL"
echo "  Short codes:  $NUM_CODES"
echo "  Requests:     $REQUESTS"
echo "  Concurrency:  $CONCURRENCY"
echo "  Timeout:      ${TIMEOUT}s"
echo "  Target:       $TARGET_RPS RPS"
echo "============================================================"
echo ""

# =============================================================================
# Run tests across multiple short codes
# =============================================================================
# Calculate requests per code (test multiple codes to simulate real traffic)
CODES_TO_TEST=10
REQUESTS_PER_CODE=$((REQUESTS / CODES_TO_TEST))

# Get random sample of codes
SAMPLED_CODES=()
for i in $(shuf -i 0-$((NUM_CODES - 1)) -n $CODES_TO_TEST); do
    SAMPLED_CODES+=("${SHORT_CODES[$i]}")
done

echo "Testing $CODES_TO_TEST random short codes ($REQUESTS_PER_CODE requests each)..."
echo ""

# Temp file for results
RESULTS_FILE=$(mktemp)
TOTAL_REQUESTS=0
TOTAL_FAILED=0
TOTAL_TIME=0
TOTAL_RPS=0

for code in "${SAMPLED_CODES[@]}"; do
    URL="$BASE_URL/$code"
    echo -n "  Testing /$code ... "
    
    # Run ab and capture output
    OUTPUT=$(ab -n "$REQUESTS_PER_CODE" -c "$CONCURRENCY" -s "$TIMEOUT" "$URL" 2>&1)
    
    # Parse results
    RPS=$(echo "$OUTPUT" | grep "Requests per second" | awk '{print $4}')
    FAILED=$(echo "$OUTPUT" | grep "Failed requests" | awk '{print $3}')
    TIME=$(echo "$OUTPUT" | grep "Time taken for tests" | awk '{print $5}')
    P50=$(echo "$OUTPUT" | grep "50%" | awk '{print $2}')
    P99=$(echo "$OUTPUT" | grep "99%" | awk '{print $2}')
    
    # Handle empty values
    RPS=${RPS:-0}
    FAILED=${FAILED:-0}
    TIME=${TIME:-0}
    
    echo "${RPS} RPS (P50: ${P50}ms, P99: ${P99}ms, Failed: $FAILED)"
    
    # Accumulate totals
    TOTAL_RPS=$(echo "$TOTAL_RPS + $RPS" | bc)
    TOTAL_FAILED=$((TOTAL_FAILED + FAILED))
    TOTAL_TIME=$(echo "$TOTAL_TIME + $TIME" | bc)
    TOTAL_REQUESTS=$((TOTAL_REQUESTS + REQUESTS_PER_CODE))
    
    # Store for averaging
    echo "$RPS" >> "$RESULTS_FILE"
done

# =============================================================================
# Calculate final statistics
# =============================================================================
AVG_RPS=$(echo "scale=2; $TOTAL_RPS / $CODES_TO_TEST" | bc)
EFFECTIVE_RPS=$(echo "scale=2; $TOTAL_REQUESTS / $TOTAL_TIME" | bc 2>/dev/null || echo "$AVG_RPS")

echo ""
echo "============================================================"
echo "  AGGREGATED RESULTS"
echo "============================================================"
echo "  Total Requests:     $TOTAL_REQUESTS"
echo "  Failed Requests:    $TOTAL_FAILED"
echo "  Total Time:         ${TOTAL_TIME}s"
echo "============================================================"
printf "  ⚡ AVG RPS:         %.2f\n" "$AVG_RPS"
echo "============================================================"

# Check target
if (( $(echo "$AVG_RPS >= $TARGET_RPS" | bc -l) )); then
    echo "  ✅ TARGET MET: $AVG_RPS RPS >= $TARGET_RPS RPS"
else
    echo "  ❌ TARGET NOT MET: $AVG_RPS RPS < $TARGET_RPS RPS"
fi
echo "============================================================"
echo ""

# =============================================================================
# Run single comprehensive test
# =============================================================================
echo "Running single high-volume test for accurate measurement..."
RANDOM_CODE=${SHORT_CODES[$RANDOM % $NUM_CODES]}
echo ""
echo "  URL: $BASE_URL/$RANDOM_CODE"
echo "  Requests: $REQUESTS"
echo "  Concurrency: $CONCURRENCY"
echo ""

ab -n "$REQUESTS" -c "$CONCURRENCY" -s "$TIMEOUT" "$BASE_URL/$RANDOM_CODE" 2>&1 | \
    grep -E "(Requests per second|Time taken|Failed|50%|95%|99%|Complete requests)"

echo ""
echo "============================================================"

# Cleanup
rm -f "$RESULTS_FILE"
