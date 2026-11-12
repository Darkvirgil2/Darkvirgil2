# Versione web del corso

`corso.html` è il libro completo (capitoli, laboratorio interattivo in JavaScript, esercizi con soluzione)
in un unico file: funziona su tablet e telefono, senza Python.

- **Per aprirlo**: il file contiene solo il corpo della pagina. Il modo più semplice è il link pubblicato su claude.ai.
  In alternativa scaricalo e aprilo in un browser: la maggior parte dei browser lo visualizza correttamente
  anche senza le intestazioni `<html>`/`<head>`.
- **Per rigenerarlo dopo aver modificato i capitoli**: `pip install markdown && python3 build.py`.
  `template.html` contiene grafica e laboratorio; i capitoli vengono presi da `../libro/`.
