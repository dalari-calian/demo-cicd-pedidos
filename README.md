# Demo CI/CD — módulo de pedidos (código legado)

Projeto de apoio ao seminário de **Manutenção e Melhoria de Software**
(Engenharia de Software, Turma B) — categoria **CI/CD**, ferramentas
**GitHub Actions / GitLab CI / Jenkins**.

## O que tem aqui

| Caminho | Papel na demo |
|---|---|
| `src/pedidos/calculadora.py` | O código legado: função longa, números mágicos, regra duplicada |
| `tests/test_calculadora.py` | A rede de segurança: 10 testes, incluindo o caso de fronteira |
| `.github/workflows/ci.yml` | Pipeline no GitHub Actions |
| `.gitlab-ci.yml` | O mesmo pipeline no GitLab CI |
| `Jenkinsfile` | O mesmo pipeline no Jenkins (DSL declarativa) |
| `scripts/quebrar-demo.sh` | Introduz a regressão do Ato 2 |
| `scripts/corrigir-demo.sh` | Corrige a regressão no Ato 3 |
| `ROTEIRO-DEMO.md` | Roteiro cronometrado da apresentação ao vivo |
| `docker-compose.jenkins.yml` | Jenkins local (plano B, sem internet) |

## Estágios do pipeline (idênticos nas três ferramentas)

1. **lint** — `flake8` sobre `src` e `tests`
2. **test** — `pytest` com cobertura e *quality gate* de 80% (`--cov-fail-under=80`)
3. **build** — empacota um artefato versionado (`pedidos-<ref>-<sha>.zip`)
4. **release/deploy** — só dispara em tag `v*`; publica o artefato e implanta

## Rodando na sua máquina

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

flake8 src tests
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

## Simulando a regressão (o coração da demo)

```bash
bash scripts/quebrar-demo.sh   # troca >= 500 por > 500
pytest                         # 1 teste falha: assert 475.0 == 450.0
bash scripts/corrigir-demo.sh  # restaura
pytest                         # 10 passed
```

## Por que isso importa para a disciplina

O pipeline não é o objetivo — é o que torna a **manutenção segura**. Com a suíte
rodando a cada push, dá para refatorar a `calcular_total` (extrair as faixas de
desconto, eliminar os números mágicos, separar o cálculo de frete) sabendo em
menos de um minuto se o comportamento externo continua o mesmo. Sem isso,
refatorar código legado é aposta.
