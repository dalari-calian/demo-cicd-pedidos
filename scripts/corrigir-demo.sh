#!/usr/bin/env bash
# ATO 3 DA DEMO - corrige a regressao apontada pelo pipeline.
set -e
sed -i 's/elif total > 500:/elif total >= 500:/' src/pedidos/calculadora.py
echo "Regressao corrigida em src/pedidos/calculadora.py"
grep -n "elif total >= 500:" src/pedidos/calculadora.py
