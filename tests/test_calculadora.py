"""Suite de testes que serve de rede de seguranca para o modulo legado."""
import pytest

from pedidos.calculadora import calcular_total


def itens(valor_unitario, quantidade=1):
    return [{"preco": valor_unitario, "qtd": quantidade}]


def test_pedido_pequeno_sem_desconto_soma_frete_do_sul():
    # 100.00 de produtos, abaixo da primeira faixa, + frete SC (15.00)
    assert calcular_total(itens(50.0, 2), uf="SC") == 115.00


def test_faixa_de_5_por_cento_a_partir_de_200():
    # 200.00 - 5% = 190.00 + frete 15.00
    assert calcular_total(itens(200.0), uf="SC") == 205.00


def test_faixa_de_10_por_cento_no_limite_exato_de_500():
    # REGRESSAO CLASSICA DE FRONTEIRA: 500 tem de entrar na faixa de 10%.
    # 500.00 - 10% = 450.00, com frete gratis (subtotal >= 300).
    assert calcular_total(itens(500.0), uf="SC") == 450.00


def test_faixa_de_15_por_cento_com_cliente_vip():
    # 1000.00 - 15% = 850.00 - 10% VIP = 765.00, frete gratis
    assert calcular_total(itens(1000.0), cliente_vip=True, uf="SC") == 765.00


def test_cupom_primeira_compra_acumula_com_a_faixa():
    # 300.00 - 5% = 285.00 - 10% = 256.50; abaixo de 300, paga frete 15.00
    assert calcular_total(itens(300.0), cupom="PRIMEIRACOMPRA", uf="SC") == 271.50


def test_cupom_frete_gratis_zera_o_frete_em_pedido_pequeno():
    assert calcular_total(itens(100.0), cupom="FRETEGRATIS", uf="SC") == 100.00


@pytest.mark.parametrize(
    "uf,esperado",
    [("SC", 115.00), ("SP", 120.00), ("AM", 135.00)],
)
def test_frete_varia_por_regiao(uf, esperado):
    assert calcular_total(itens(100.0), uf=uf) == esperado


def test_pedido_vazio_cobra_apenas_o_frete():
    assert calcular_total([], uf="SC") == 15.00
