"""Modulo legado de calculo de pedidos.

ATENCAO (proposital): este arquivo representa o "codigo legado" da demo.
Ele funciona, mas tem os smells classicos de manutencao:
  - funcao longa, com varias responsabilidades misturadas;
  - numeros magicos espalhados (0.15, 500, 300, 35.0...);
  - regra de desconto duplicada em mais de um ponto;
  - estados de UF codificados na mao dentro da funcao.

O objetivo da demo NAO e refatorar isso ao vivo, e sim mostrar que so da
para refatorar com seguranca depois que existe uma suite rodando no pipeline.
"""


def calcular_total(itens, cliente_vip=False, cupom=None, uf="SC"):
    """Calcula o valor final de um pedido (produtos - descontos + frete)."""
    total = 0.0
    for item in itens:
        total = total + item["preco"] * item["qtd"]

    # desconto por faixa de valor
    if total >= 1000:
        total = total - total * 0.15
    elif total >= 500:
        total = total - total * 0.10
    elif total >= 200:
        total = total - total * 0.05

    # desconto de cliente VIP
    if cliente_vip:
        total = total - total * 0.10

    # cupons
    if cupom == "PRIMEIRACOMPRA":
        total = total - total * 0.10

    # frete por regiao
    if uf in ("SC", "PR", "RS"):
        frete = 15.0
    elif uf in ("SP", "RJ", "MG", "ES"):
        frete = 20.0
    else:
        frete = 35.0

    # frete gratis
    if total >= 300 or cupom == "FRETEGRATIS":
        frete = 0.0

    return round(total + frete, 2)
