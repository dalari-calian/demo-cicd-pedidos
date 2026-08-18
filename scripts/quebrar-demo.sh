#!/usr/bin/env bash
# ATO 2 DA DEMO - introduz uma regressao classica de fronteira.
# Troca "total >= 500" por "total > 500": quem compra exatamente 500 perde
# a faixa de 10% e cai na de 5%. Nenhum lint pega isso; so o teste pega.
set -e
sed -i 's/elif total >= 500:/elif total > 500:/' src/pedidos/calculadora.py
echo "Regressao aplicada em src/pedidos/calculadora.py"
grep -n "elif total > 500:" src/pedidos/calculadora.py
