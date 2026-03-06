"""
Agent Akinator - Un jeu de devinettes interactif

L'agent pose des questions pour deviner à quoi vous pensez.
Catégories : Personnages, Objets, Animaux
Réponses possibles : Oui, Non, Ne sais pas, Probablement, Probablement pas

"""

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


def create_akinator_agent(category: str):
    """
    Crée l'agent Akinator qui devine ce à quoi vous pensez.
    
    Args:
        category: La catégorie choisie (Personnages, Objets, ou Animaux)
    
    Returns:
        Un agent configuré pour jouer à Akinator
    """
    
    # Modèle LLM
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
        temperature=0.75 
    )

    # Prompt système pour l'agent Akinator
    system_prompt = f"""Tu es Akinator, un génie qui devine à quoi les gens pensent en posant des questions.

CONTEXTE :
- La personne pense à quelque chose dans la catégorie : {category}
- Tu dois deviner en posant des questions intelligentes et stratégiques
- Commence par des questions larges, puis affine progressivement

RÉPONSES POSSIBLES DE L'UTILISATEUR :
- "Oui" : la réponse est clairement oui
- "Non" : la réponse est clairement non
- "Ne sais pas" : l'utilisateur ne sait pas ou n'est pas sûr
- "Probablement" : la réponse est probablement oui
- "Probablement pas" : la réponse est probablement non

TON COMPORTEMENT :
1. Pose UNE SEULE question à la fois, claire et précise
2. Base-toi sur toutes les réponses précédentes pour affiner tes questions
3. Commence par des questions générales (genre, époque, domaine, etc.)
4. Affine progressivement avec des questions plus spécifiques
5. Prends en compte les nuances : "Probablement" et "Probablement pas" indiquent une incertitude
6. Après environ 15-20 questions, ou quand tu es très confiant, fais une proposition :
   "Je pense que c'est [ta proposition] ! Est-ce correct ?"
7. Si ta proposition est fausse, continue à poser des questions

FORMAT DE TES MESSAGES :
- Pour une question : Pose simplement ta question
- Pour une proposition : "Je pense que c'est [X] ! Est-ce correct ?"
- Si tu gagnes : "J'ai gagné ! C'était bien [X] ! 🎉"
- Garde un ton amical et mystérieux

STRATÉGIE :
- Pour les Personnages : demande le domaine (fiction/réel), l'époque, le genre, la nationalité, etc.
- Pour les Objets : demande l'usage, la taille, le matériau, où on le trouve, etc.
- Pour les Animaux : demande le type (mammifère, oiseau, etc.), l'habitat, la taille, domestique ou sauvage, etc.
"""

    # Création de l'agent avec mémoire
    checkpointer = MemorySaver()
    
    agent = create_agent(
        model=model,
        tools=[],  # Pas besoin d'outils externes pour ce jeu
        system_prompt=system_prompt,
        checkpointer=checkpointer
    )
    
    return agent


def play_akinator():
    """
    Lance une partie interactive d'Akinator dans le terminal
    """
    print("=" * 60)
    print("BIENVENUE DANS AKINATOR")
    print("=" * 60)
    print("\nJe vais deviner à quoi vous pensez en vous posant des questions !")
    print("\nChoisissez une catégorie :")
    print("1. Personnages (réels ou fictifs)")
    print("2. Objets")
    print("3. Animaux")
    
    while True:
        choice = input("\nVotre choix (1/2/3) : ").strip()
        if choice == "1":
            category = "Personnages"
            break
        elif choice == "2":
            category = "Objets"
            break
        elif choice == "3":
            category = "Animaux"
            break
        else:
            print("Choix invalide. Veuillez choisir 1, 2 ou 3.")
    
    print(f"\nTrès bien ! Pensez à un(e) {category.lower()} et je vais essayer de deviner !")
    print("\nRéponses possibles : Oui / Non / Ne sais pas / Probablement / Probablement pas")
    input("\nQuand vous êtes prêt(e), appuyez sur Entrée...")
    
    # Créer l'agent
    agent = create_akinator_agent(category)
    
    # Configuration pour maintenir la conversation
    config = {"configurable": {"thread_id": "akinator_game_1"}}
    
    # Démarrer la conversation
    print("\n" + "=" * 60)
    print("LA PARTIE COMMENCE")
    print("=" * 60 + "\n")
    
    # Première question de l'agent
    response = agent.invoke({
        "messages": [HumanMessage(content="Commence le jeu en posant ta première question.")]
    }, config)
    
    agent_message = response['messages'][-1].content
    print(f"Akinator : {agent_message}\n")
    
    question_count = 1
    
    # Boucle de jeu
    while True:
        user_input = input("Vous : ").strip()
        
        if not user_input:
            print("Veuillez entrer une réponse.\n")
            continue
        
        # Commandes spéciales
        if user_input.lower() in ['quit', 'quitter', 'exit', 'stop']:
            print("\nMerci d'avoir joué ! À bientôt !")
            break
        
        # Envoyer la réponse à l'agent
        response = agent.invoke({
            "messages": [HumanMessage(content=user_input)]
        }, config)
        
        agent_message = response['messages'][-1].content
        
        # Vérifier si l'agent a gagné
        if "j'ai gagné" in agent_message.lower():
            print(f"\nAkinator : {agent_message}")
            print("\n" + "=" * 60)
            print("PARTIE TERMINÉE")
            print("=" * 60)
            break
        
        question_count += 1
        print(f"\nAkinator : {agent_message}\n")
        
        # Limiter le nombre de questions pour éviter les boucles infinies
        if question_count > 50:
            print("\nLimite de questions atteinte ! Partie terminée.")
            break
    
    # Proposer de rejouer
    print("\n" + "=" * 60)
    rejouer = input("\nVoulez-vous rejouer ? (oui/non) : ").strip().lower()
    if rejouer in ['oui', 'o', 'yes', 'y']:
        print("\n" * 2)
        play_akinator()


if __name__ == "__main__":
    # Lancer le jeu interactif
    play_akinator()
    
    # Pour tester sans interaction :
    # test_akinator()
