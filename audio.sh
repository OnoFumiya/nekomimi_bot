#!/bin/bash

echo "╔══╣ Setup: NekoMimi Bot Audio(STARTING) ╠══╗"


# Keep track of the current directory
DIR=`pwd`

# Install TTS packages for OpenPico
cd ../sobits_tts/install/
bash openpico.sh
cd ../..

cd sobits_speech_recognition/install/
bash sherpa.sh
cd ../..

MODEL_NAME="sherpa-onnx-nemo-parakeet-tdt_ctc-0.6b-ja-35000-int8"
BASE_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models"
INSTALL_DIR="$HOME/.sobits_speech_recognition/sherpa_models"

ARCHIVE_TAR="${MODEL_NAME}.tar.bz2"
ARCHIVE_GZ="${MODEL_NAME}.tar.gz"
ARCHIVE_ZIP="${MODEL_NAME}.zip"

echo "=== Sherpa-ONNX Model Installer ==="
echo "Model: $MODEL_NAME"
echo "Install dir: $INSTALL_DIR"

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

if [ -d "$MODEL_NAME" ]; then
    echo "Model already installed. Skipping."
    exit 0
fi

download_success=false

for FILE in "$ARCHIVE_TAR" "$ARCHIVE_GZ" "$ARCHIVE_ZIP"; do
    URL="${BASE_URL}/${FILE}"
    echo "Trying: $URL"

    if curl -fL -o "$FILE" "$URL"; then
        ARCHIVE_FILE="$FILE"
        download_success=true
        break
    else
        echo "Not found: $FILE"
        rm -f "$FILE"
    fi
done

if [ "$download_success" = false ]; then
    echo "ERROR: Model archive not found."
    exit 1
fi

echo "Extracting: $ARCHIVE_FILE"

if [[ "$ARCHIVE_FILE" == *.tar.bz2 ]] || [[ "$ARCHIVE_FILE" == *.tar.gz ]]; then
    tar -xf "$ARCHIVE_FILE"
elif [[ "$ARCHIVE_FILE" == *.zip ]]; then
    unzip "$ARCHIVE_FILE"
else
    echo "Unknown archive format"
    exit 1
fi

rm "$ARCHIVE_FILE"

# Go back to previous directory
cd ${DIR}


echo "╚══╣ Setup: NekoMimi Bot Audio (FINISHED) ╠══╝"
