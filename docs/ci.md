# CI och schemaläggning

`.github/workflows/validate.yml` kör på push till main och PR. Tre GitHub-hostade
Ubuntu-jobb kör Python3.13/compileall/pytest, Hassfest respektive HACS:s integration-
validering. `.github/workflows/security-audit.yml` kör Gitleaks med redigerad output
på hela Git-historiken vid PR, manuellt och den4:e varje månad02:17UTC. Dessa kontroller
är inte en full säkerhetsanalys av behörigheter eller en HA-integrationstestmiljö.

Det publika repot använder inga beständiga self-hosted-runners för PR-kod. Fork-PR:er
kan därför få samma grundkontroller utan att köras på hemnets VM. Jobs har contents:read,
checkout utan sparade credentials och saknar installationshemligheter. Privata reusable
workflows i wp-plugin-ci kan inte användas direkt av detta publika repo.

## Granskning av aktuell commit

`code-review.yml` kör en API-baserad grind hos GitHub vid PR, PR-kommentar, manuellt
och var15:e minut. `pull_request_target` får endast läsa GitHubs PR-/kommentar-API och
skriva commitstatus; workflowet checkar aldrig ut eller kör kod från PR:n. En kommentar
från en mänsklig användare med aktuell write/maintain/admin-behörighet
(kontrollerad genom GitHubs API) godkänner endast exakt SHA med en egen rad:

```text
<!-- manual-review:FULLSTÄNDIG-GRANSKAD-SHA -->
```

Granska faktisk diff och berörda anropsvägar, åtgärda fynd och skriv vilka kontroller
som körts innan markören postas. Kontrollera PR:ns head-SHA en gång till vid postning.
Ny push ger en ny SHA utan godkännande; radering av kommentaren tar bort godkännandet
vid nästa grindkörning. Markören är ett mänskligt intyg, inte bevis på automatisk AI-
granskning. Merge kräver avstämning av alla aktuella checkar, inklusive Kodgranskning.

## Månadsgranskning

Schemat finns i det privata repot `agrolsy-org/wp-plugin-ci`, i
`.github/workflows/monthly-public-review.yml`. Workflowet hämtar publika
källans main läsande och kör den gemensamma AI-granskningen på `org-codex-review` på
Sambandscentralen. GitHub äger cronstarten; utvecklarens dator behöver inte vara på.
Findings och rapporter finns i det privata core-repot, med källrepo/SHA i rapporten.
En separat daglig GitHub-hostad watchdog bevakar misslyckade/uteblivna körningar.

Ändringar här startar inte om HA, installerar inte integrationen och bevisar inte att
en verklig backup, uppgradering eller frontend har testats på hemnets installation.
