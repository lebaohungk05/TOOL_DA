#!/bin/bash
TARGET_DIR=$1
INDEX_FILE="${TARGET_DIR}/index.md"

echo "# Index: $(basename "${TARGET_DIR}")" > "${INDEX_FILE}"
echo "" >> "${INDEX_FILE}"

for f in "${TARGET_DIR}"/*.md; do
    if [ "$(basename "$f")" != "index.md" ]; then
        echo "<!-- Imported from: ./$(basename "$f") -->" >> "${INDEX_FILE}"
        cat "$f" >> "${INDEX_FILE}"
        echo "" >> "${INDEX_FILE}"
        echo "<!-- End of import from: ./$(basename "$f") -->" >> "${INDEX_FILE}"
        echo "" >> "${INDEX_FILE}"
    fi
done
