#!/bin/bash
chmod a-w *
for filename in */*; do
    chmod a-w "$filename"
    echo "$filename"
done
chmod a-w *
chmod a-w .