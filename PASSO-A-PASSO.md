# Passo a passo — CI/CD com GitHub Actions

Guia do zero até o release publicado. Cada parte tem **o que fazer** e **o que dizer**
(o "por quê", que é o que a banca pergunta).

---

## Parte 0 — Pré-requisitos (fazer em casa, com calma)

### 0.1 Conta no GitHub
Criar em <https://github.com/signup>. Nada pago: Actions é gratuito e ilimitado em
repositório público.

### 0.2 Git instalado

```bash
git --version
```

Se não aparecer versão: `sudo apt install git` (Linux), `brew install git` (macOS),
ou <https://git-scm.com/downloads> (Windows — instale o **Git Bash**, você vai
precisar dele para rodar os scripts `.sh`).

### 0.3 Identidade do Git

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```

### 0.4 Autenticação (o passo que trava mais gente)

O GitHub **não aceita senha** no `git push` desde 2021. Escolha um dos dois:

**Opção A — HTTPS com token (mais simples)**
1. <https://github.com/settings/tokens> → *Generate new token (classic)*
2. Marcar o escopo **repo**; expiração 30 dias basta
3. Copiar o token (aparece uma única vez)
4. No primeiro `git push`, quando pedir senha, **cole o token** no lugar da senha

**Opção B — SSH (não pede nada depois de configurado)**
```bash
ssh-keygen -t ed25519 -C "seu@email.com"   # Enter em tudo
cat ~/.ssh/id_ed25519.pub                  # copiar a saída inteira
```
Colar em <https://github.com/settings/keys> → *New SSH key*. Testar:
```bash
ssh -T git@github.com
```

### 0.5 Python e as dependências locais

```bash
python3 --version                # precisa ser 3.9+
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Parte 1 — Entender o `ci.yml` antes de rodar

O arquivo `.github/workflows/ci.yml` **é** a sua implementação de CI/CD. Não existe
servidor para instalar: o GitHub já mantém um, e esse arquivo é o programa que ele
executa. Vocabulário mínimo, na ordem em que aparece no arquivo:

### `on:` — o gatilho (evento)

```yaml
on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:
    branches: [main]
```

É a resposta para "quando isso roda?". Todo `git push` na `main` dispara; toda tag
que começa com `v` dispara; todo pull request para a `main` dispara. Nenhum humano
clica em nada — é o evento do Git que aciona.

### `jobs:` — as unidades de execução

Cada job roda em uma **máquina virtual limpa e descartável** (`runs-on:
ubuntu-latest`), que é criada, clona seu código, executa os passos e é destruída.
Por isso todo job precisa refazer o `pip install`: nada persiste entre eles.

### `needs:` — a ordem (DAG)

```yaml
test:
  needs: lint
```

Sem `needs`, jobs rodam em paralelo. Com `needs`, viram uma corrente: `lint → test →
build → release`. Se o lint falha, o resto nem começa — economiza tempo e deixa claro
o que quebrou.

### `steps:` e `uses:` — os passos e as ações reutilizáveis

```yaml
- uses: actions/checkout@v4      # baixa seu código para dentro da VM
- uses: actions/setup-python@v5  # instala o Python 3.11
- run: pip install -r requirements.txt
```

`uses` chama uma **action** pronta do marketplace (código de terceiros, versionado
por tag). `run` executa comando de shell direto.

### O *quality gate* — o coração do requisito

```yaml
run: pytest --cov=src --cov-fail-under=80 --junitxml=relatorio-testes.xml
```

Não existe mágica: **o gate é o código de saída do processo**. O `pytest` retorna
diferente de zero se algum teste falhar *ou* se a cobertura ficar abaixo de 80%; o
runner vê esse código e marca o job como vermelho. Foi por isso que a fábrica de
software inteira convergiu para "exit code": é o contrato universal entre qualquer
ferramenta e qualquer pipeline.

Neste projeto a cobertura atual é de **100%** (22 statements, 0 miss), então o gate de
80% tem folga — ele existe para pegar regressão futura, não para reprovar hoje.

### `if: always()` — publicar o diagnóstico mesmo no vermelho

```yaml
- name: Publicar relatorio de diagnostico
  if: always()
```

Sem isso, quando o teste falha o passo seguinte é pulado e você perde justamente o
relatório de que precisa para diagnosticar. Detalhe pequeno, conceito importante:
**pipeline que quebra em silêncio não serve**.

### `if:` no job `release` — a diferença entre integrar e liberar

```yaml
release:
  if: startsWith(github.ref, 'refs/tags/v')
```

Os três primeiros jobs rodam a cada push (isso é **integração** contínua). O `release`
só roda quando o evento é uma tag `v*` (isso é **liberação** contínua). É a fronteira
conceitual que o requisito da atividade pede.

---

## Parte 2 — Criar o repositório e subir o projeto

### 2.1 Criar o repositório vazio no GitHub

<https://github.com/new> → nome `demo-cicd-pedidos` → **Public** →
**não** marcar "Add a README file" (o projeto já tem um) → *Create repository*.

### 2.2 Conferir a estrutura local

Entre na pasta do projeto e confirme que ela está **exatamente** assim:

```
demo-cicd-pedidos/
├── .github/workflows/ci.yml      <- caminho exato, senão o Actions ignora
├── .gitignore
├── .gitlab-ci.yml
├── Jenkinsfile
├── README.md
├── ROTEIRO-DEMO.md
├── docker-compose.jenkins.yml
├── requirements.txt
├── setup.cfg
├── src/pedidos/__init__.py
├── src/pedidos/calculadora.py
├── tests/test_calculadora.py
└── scripts/quebrar-demo.sh
    scripts/corrigir-demo.sh
```

O caminho `.github/workflows/` não é negociável: é onde o GitHub procura workflows. Um
`ci.yml` na raiz simplesmente não é executado, e não aparece nenhum aviso.

Verificação rápida:
```bash
ls -a
ls .github/workflows
```

### 2.3 Rodar tudo localmente antes (evita subir vermelho)

```bash
flake8 src tests
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

Esperado: `10 passed`, cobertura 100%. Se passa aqui, passa no runner — é o mesmo
comando.

### 2.4 Primeiro push

```bash
git init
git branch -M main
git add .
git commit -m "feat: modulo de pedidos com pipeline de CI/CD"
git remote add origin https://github.com/SEU-USUARIO/demo-cicd-pedidos.git
git push -u origin main
```

(Se escolheu SSH na parte 0.4, a URL é `git@github.com:SEU-USUARIO/demo-cicd-pedidos.git`.)

---

## Parte 3 — Ato 1: o pipeline verde

Abra o repositório no navegador e clique na aba **Actions**. O workflow já vai estar
rodando — o push foi o gatilho.

Clique na execução para ver o grafo `lint → test → build` e abra cada job para ver o
log ao vivo.

**O que mostrar:** que ninguém clicou em "rodar"; a sequência dos estágios; o artefato
`pacote-pedidos` disponível para download no final da página; o tempo total
(~40–60 s).

**O que dizer:** "Feedback completo em menos de um minuto, sem ninguém rodar nada na
mão."

> Enquanto o job roda, **fale**. Nunca espere em silêncio — explique o que cada
> estágio faz. É o intervalo mais valioso da apresentação.

---

## Parte 4 — Ato 2: quebrar de propósito

```bash
bash scripts/quebrar-demo.sh
git diff
git commit -am "fix: ajusta faixa de desconto de 500 reais"
git push
```

O script troca uma única linha em `src/pedidos/calculadora.py`:
`elif total >= 500:` vira `elif total > 500:`. Um cliente que compra exatamente
R$ 500 deixa de entrar na faixa de 10% e cai na de 5% — paga R$ 25 a mais.

**O que mostrar:** o diff de uma linha; o `lint` passando **verde** (estilo não pega
regra de negócio errada); o `test` em **vermelho**; o job `build` nem tendo sido
iniciado, por causa do `needs`.

**O que dizer:** "É o clássico erro de fronteira. Nenhuma revisão manual apressada
pegaria isso. O pipeline pegou em 40 segundos."

Este é o momento mais forte da demonstração. É a prova de que existe uma classe de
defeito que **só** o teste automatizado captura.

---

## Parte 5 — Ato 3: diagnóstico e correção

Abra o job **Testes + quality gate de cobertura** → passo `pytest`. O log mostra
exatamente:

```
FAILED tests/test_calculadora.py::test_faixa_de_10_por_cento_no_limite_exato_de_500
E   AssertionError: assert 475.0 == 450.0
```

Traduza em voz alta: *"o pipeline não diz só que quebrou — diz qual regra, qual
linha e qual valor. 475 onde devia ser 450."*

Desça também até a tabela de cobertura por arquivo, que sai no mesmo log, e mencione
os artefatos `relatorio-testes.xml` e `coverage.xml` publicados pelo `if: always()`.

Corrigir:

```bash
bash scripts/corrigir-demo.sh
git commit -am "fix: restaura o limite inclusivo da faixa de 10%"
git push
```

**O que mostrar:** o pipeline voltando ao verde no mesmo lugar.

---

## Parte 6 — Ato 4: liberar a versão

```bash
git tag -a v1.1.0 -m "Correcao da faixa de desconto de 500"
git push origin --tags
```

Volte para a aba Actions: uma **nova execução** começou, disparada pela tag — e nela
o job `release` aparece, o que não acontecia nas execuções anteriores.

Quando terminar, vá na aba **Releases** (coluna direita da página inicial do repo):
está lá o `pedidos-v1.1.0-<sha>.zip`, versionado e público.

**O que dizer:** "O artefato que foi testado é exatamente o que vai para o ambiente —
build once, deploy many. E o rollback é reimplantar a tag anterior, que continua
publicada."

**Seja honesto sobre o deploy:** o passo final é um `echo` — ambiente simulado. O que
é real e verificável é a *liberação*: um artefato imutável, versionado, publicado
automaticamente. Dizer isso abertamente é mais forte que deixar a banca descobrir.

---

## Parte 7 — Mapa requisito → evidência na tela

Leve isto anotado. É o que transforma a demo em resposta ao enunciado.

| Requisito | Onde a evidência aparece |
|---|---|
| Integração contínua | aba Actions disparando sozinha no push |
| Testes automatizados | job `test`, 10 testes |
| Quality gate | `--cov-fail-under=80` derrubando o build pelo exit code |
| Detecção de regressão | `assert 475.0 == 450.0` no log |
| Relatório de diagnóstico | artefatos `relatorio-testes.xml` / `coverage.xml` |
| Geração de versão | `pedidos-v1.1.0-<sha>.zip` |
| Liberação contínua | job `release` disparando só na tag `v*` |
| Entrega vs implantação | `release` automático aqui × `when: manual` no GitLab |
| Três ferramentas | `ci.yml`, `.gitlab-ci.yml` e `Jenkinsfile` no repositório |

Sobre a última linha: mantenha os três arquivos no repositório mesmo executando apenas
o GitHub. Abra os três lado a lado num slide e mostre que os estágios são os mesmos —
muda a sintaxe (YAML de workflow, YAML de stages, DSL Groovy com controller e agents),
não o conceito. Isso responde "por que estas ferramentas?" sem você precisar manter um
Jenkins de pé.

---

## Parte 8 — Se der problema

| Sintoma | Causa provável | Solução |
|---|---|---|
| Aba Actions vazia | `ci.yml` fora de `.github/workflows/` | mover para o caminho exato |
| Nada dispara ao dar push | push feito em outra branch | trabalhar na `main` |
| `git push` rejeitado por senha | senha em vez de token | usar token (0.4 A) ou SSH (0.4 B) |
| `ModuleNotFoundError: pedidos` | rodou pytest fora da raiz | rodar na pasta com `setup.cfg` |
| `sed: -i may not be used...` | script rodado no macOS | usar `sed -i ''` ou rodar no Linux/Codespaces |
| Job `release` não aparece | tag não foi enviada | `git push origin --tags` |
| `gh: not found` no release | job rodando fora do runner do GitHub | manter `runs-on: ubuntu-latest` |
| Scripts `.sh` no Windows | `cmd` não roda bash | usar o **Git Bash** |

---

## Parte 9 — Refinamentos opcionais (só se sobrar tempo)

Nada aqui é necessário para atender ao requisito. São o que rende ponto extra:

1. **Pull request com merge bloqueado.** Criar branch, abrir PR, e em
   *Settings → Rules → Rulesets* exigir o status check "Testes + quality gate de
   cobertura". Aí o botão de merge fica travado no vermelho — visualmente muito
   convincente. Exige configuração manual, então faça só depois que o básico
   estiver ensaiado.
2. **Badge de status no README.** Actions → workflow → *Create status badge*. Cola
   um selo verde no topo do repositório.
3. **Refatorar a `calcular_total`** ao vivo (extrair as faixas, eliminar os números
   mágicos) com o pipeline confirmando que o comportamento externo não mudou. É o
   fechamento perfeito para uma disciplina de Manutenção de Software: o pipeline não
   é o objetivo, é o que torna a refatoração segura.

---

## Cronograma sugerido

| Quando | O quê |
|---|---|
| 3 dias antes | Partes 0 a 3: conta, token, push, primeiro verde |
| 2 dias antes | Partes 4 a 6 completas, uma vez, sem pressa |
| 1 dia antes | Ensaio cronometrado (0:45 / 1:00 / 1:15 / 1:00) + gravar vídeo de reserva |
| No dia | Repositório, aba Actions e terminal já abertos em abas separadas |

Deixe os comandos de cada ato colados em um arquivo de texto e leia de lá. Digitar
comando ao vivo, sob pressão, é a causa número um de demo travada.
