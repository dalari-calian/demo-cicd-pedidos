# Roteiro da demonstração prática (4 minutos)

Seminário de **Manutenção e Melhoria de Software** — Categoria CI/CD
Gabriel Queiroz · Calian Dalari · Erik Locatelli · Ricardo Cardoso

---

## Antes de começar (fazer na véspera, não na hora)

1. Criar o repositório no GitHub (e, se for mostrar as três, espelhar no GitLab).
2. Subir este projeto e **confirmar que o primeiro pipeline ficou verde**.
3. Deixar abertas, em abas separadas:
   - o repositório com o arquivo `src/pedidos/calculadora.py`;
   - a aba **Actions** (ou **CI/CD → Pipelines**, no GitLab);
   - o terminal já dentro da pasta do projeto, com `git` configurado;
   - o Jenkins local em `http://localhost:8080` (plano B, ver seção final).
4. Ensaiar uma vez cronometrado. O pipeline leva ~40-60 s por execução: **fale enquanto ele roda**, nunca espere em silêncio.

> Dica: rode `git push` do Ato 2 logo antes de começar o Ato 1 não é possível — mas você pode **deixar a execução do Ato 2 já gravada em vídeo** como reserva, caso a rede caia.

---

## Ato 1 — Pipeline verde (0:45)

**O que dizer:** "Este é o código legado: um cálculo de pedido com desconto por faixa, cupom e frete. Ele já está sob CI."

```bash
git checkout -b demo-seminario
echo "" >> README.md
git commit -am "docs: ajuste no README para acionar o pipeline"
git push -u origin demo-seminario
```

**O que mostrar na tela:**
- o pipeline iniciando sozinho (ninguém clicou em nada — foi o webhook do push);
- os estágios em sequência: `lint` → `test` → `build`;
- o artefato `pedidos-*.zip` publicado ao final;
- o tempo total de execução.

**Frase de fechamento:** "Feedback completo em menos de um minuto, sem ninguém rodar nada na mão."

---

## Ato 2 — Quebrar de propósito (1:00)

**O que dizer:** "Agora vou fazer o que todo mundo já fez: uma alteração pequena, aparentemente inofensiva, em código legado."

```bash
bash scripts/quebrar-demo.sh
git diff            # mostrar o diff na tela: >= virou >
git commit -am "fix: ajusta faixa de desconto de 500 reais"
git push
```

**O que mostrar na tela:**
- o diff: uma única linha, `elif total >= 500:` virou `elif total > 500:`;
- o `lint` passando (verde) — **estilo não pega regra de negócio errada**;
- o `test` falhando (vermelho);
- se estiver em pull request: o botão de merge **bloqueado** pelo gate.

**Frase de fechamento:** "É o clássico erro de fronteira. Nenhuma revisão manual apressada pegaria isso — o pipeline pegou em 40 segundos."

---

## Ato 3 — Diagnóstico e correção (1:15)

**O que dizer:** "O pipeline não só diz que quebrou: ele diz exatamente o quê."

**O que mostrar na tela — abrir o log do job de teste:**

```
FAILED tests/test_calculadora.py::test_faixa_de_10_por_cento_no_limite_exato_de_500
E   AssertionError: assert 475.0 == 450.0
```

Traduzir para a turma: *"um cliente que comprasse exatamente R$ 500 pagaria R$ 25 a mais. Isso iria para produção sem o pipeline."*

Mostrar também, no mesmo relatório, o percentual de cobertura por arquivo.

```bash
bash scripts/corrigir-demo.sh
git commit -am "fix: restaura o limite inclusivo da faixa de 10%"
git push
```

**O que mostrar:** o mesmo pull request voltando ao verde e o merge sendo liberado.

**Frase de fechamento:** "Entrada, relatório de diagnóstico e correção — tudo dentro do mesmo ciclo, sem sair do repositório."

---

## Ato 4 — Liberação contínua (1:00)

**O que dizer:** "Com o tronco verde, liberar deixa de ser um evento de risco."

```bash
git checkout main
git merge demo-seminario
git tag -a v1.1.0 -m "Correcao da faixa de desconto de 500"
git push origin main --tags
```

**O que mostrar na tela:**
- o job `release` disparando **apenas** por causa da tag (`if: startsWith(github.ref, 'refs/tags/v')`);
- o pacote versionado publicado na aba Releases;
- no GitLab, o job `deploy_producao` esperando aprovação manual — a diferença entre **entrega** contínua e **implantação** contínua.

**Frase de fechamento:** "O artefato que foi testado é exatamente o que vai para o ambiente. E o rollback é reimplantar a tag anterior, que continua publicada."

---

## Plano B (se a rede falhar)

Jenkins local, sem depender de internet no momento da apresentação:

```bash
docker compose -f docker-compose.jenkins.yml up -d
# senha inicial:
docker exec jenkins-demo cat /var/jenkins_home/secrets/initialAdminPassword
```

Depois: **New Item → Pipeline → Pipeline script from SCM**, apontando para o repositório local. Os quatro atos funcionam igual, porque o `Jenkinsfile` tem os mesmos estágios.

Reserva final: vídeo gravado da execução do GitHub Actions (gravar na véspera).

---

## Erros comuns que derrubam a demo

| Risco | Prevenção |
|---|---|
| Esquecer o `git push` e ficar esperando o pipeline | Colar os comandos em um arquivo e ler de lá |
| Pipeline lento por instalar dependência do zero | O cache de pip já está configurado nos três arquivos |
| Falar em silêncio enquanto o job roda | Enquanto roda, explicar o que cada estágio faz |
| Estourar os 4 minutos | Cronometrar: 0:45 / 1:00 / 1:15 / 1:00 |
| Rede da faculdade bloqueando o GitHub | Testar antes; deixar Jenkins local e vídeo prontos |
