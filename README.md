# LLM-Games

## Objectif

Etant joueurs de jeux de sociétés, nous avons souhaité intégrer des agents comme joueurs de jeux. 

Les LLM étant trop forts pour des jeux de logiques ou de mémoire, nous nous sommes dit qu'il pourrait être ingénieux de leur faire prendre le rôle de narrateur ou de preneurs de décisions sur certains jeux requirant une personne "passive", externe au jeu.

## Jeux proposés

### Akinator

Le principe de ce jeu est d'essayer de deviner à quel objet ou quel personnage le joueur pense, via une série de questions posées par le logiciel.

Vous pouvez penser à un personnage, un objet ou un animal, et l'agent tentera de le deviner par une série de questions dont le principe est que vous ne répondiez que par "Oui", "Non" ou une réponse du type "Je ne sais pas" ou "Pas pertinent".
L'agent proposera parfois des tentatives de solutions en fonctions de vos réponses, vous lui direz si oui ou non c'est cela.

La partie se termine lorsque l'agent a trouvé ce à quoi vous pensez.

### Black Stories

Les Black Stories sont des histoires lugubres, souvent macabres. Il s’agit généralement de crimes / énigmes que le joueur s’efforcera de résoudre. Ces histoires plus ou moins connues sont énoncées par le narrateur, ici le LLM qui connaît la réponse de l’énigme.

Vous, joueur, devrez poser des questions en lien avec la situation de départ mystérieuse du narrateur afin d'en déceler tous les secrets, des questions qui ne pourront être répondues que par "Oui", "Non" ou "Pas pertinent".

La partie se termine lorsque vous avez trouvé l'énigme se cachant derrière la situation de départ.

## Fonctionnement

Créez à la racine du projet, un fichier `.env` avec vos tokens d'accès LLM, idéalement via Groq car la limite de tokens est plus élevée.

PS : Le modèle qwen3-32b a été testé et propose un bon équilibre en terme de pertinence, questions posées, rapidité et limite quotidienne.

```bash
# === GROQ ===
AI_API_KEY=gsk_xxx
AI_MODEL=qwen/qwen3-32b
AI_ENDPOINT=https://api.groq.com/openai/v1
```

Exécutez ensuite le fichier `games_hub.py`, choisissez votre jeu et amusez-vous !