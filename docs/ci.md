# CI och schemaläggning

`.github/workflows/validate.yml` kör på push till main och PR. Fyra GitHub-hostade
Ubuntu-jobb ingår, var och en för sig:

- `tests`: Python 3.13, compileall och pytest.
- `regression-resultat`: mergeskyddets check Regressionstester genomförda.
- `hassfest`: Home Assistants hassfest.
- `hacs`: HACS:s integrationsvalidering.

Mergeskyddets check Regressionstester genomförda beror på det faktiska
pytest-jobbet (`tests`) och blir röd även om det jobbet avbryts eller hoppas över. `.github/workflows/security-audit.yml` kör Gitleaks med redigerad output
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

## Release och versionssynkning

Versionen finns på tre ställen som alltid ska vara lika:

- `version` i `custom_components/blomster_maintenance/manifest.json`
- `?v=` i `CARD_URL` i `custom_components/blomster_maintenance/frontend.py` (cache-bust för kortet)
- raden `Version X.Y.Z hanterar bland annat` i `README.md` samt versionen i `docs/architecture.md`

`tests/test_release_contract.py` läser dessa värden och körs av pytest-jobbet, så en
osynkad version gör PR:n röd. Kontrollen ändrar inget.

Checklista vid release:

1. Höj versionen på alla tre ställen i samma PR och uppdatera dokumentationsversionen.
2. Vänta på gröna checkar (pytest, hassfest, hacs, kodgranskning) och merga till main.
3. Skapa en tagg `vX.Y.Z` på merge-commiten och en GitHub-release med samma namn. HACS
   läser releaser från repot; utan release visar HACS standardgrenens senaste commit.
4. Uppdatera i HACS på hemmets HA, starta om HA och hård-ladda webbläsaren så att det
   nya `?v=` hämtar kortet. Kontrollera Store, entiteter och kortet.
5. Återställning: publicera en ny patchrelease som återställer föregående kod med ny
   version (även `?v=`, annars behåller webbläsaren det cachade kortet). Ta aldrig bort
   eller flytta en publicerad tagg. Lagringsformatet beskrivs i `docs/storage.md`.
