import os
import re
import uuid
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# ==========================================
# OUTILS COMMUNS
# ==========================================
def log_game(message):
    """Affiche dans la console ET écrit dans game.txt (utile pour Black Stories)"""
    print(message)  
    with open("game.txt", "a", encoding="utf-8") as f:
        f.write(str(message) + "\n")

# ==========================================
# JEU 1 : AKINATOR
# ==========================================
def create_akinator_agent(category: str):
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
        temperature=0.75 
    )

    system_prompt = f"""Tu es Akinator, un génie qui devine à quoi les gens pensent en posant des questions.
CONTEXTE :
- La personne pense à quelque chose dans la catégorie : {category}
- Tu dois deviner en posant des questions intelligentes et stratégiques

RÉPONSES POSSIBLES :
- "Oui", "Non", "Ne sais pas", "Probablement", "Probablement pas"

TON COMPORTEMENT :
1. Pose UNE SEULE question à la fois, claire et précise.
2. Base-toi sur toutes les réponses précédentes.
3. Après environ 15-20 questions, ou quand tu es très confiant, fais une proposition :
   "Je pense que c'est [ta proposition] ! Est-ce correct ?"
4. Si tu gagnes, réponds EXACTEMENT en incluant la phrase : "J'ai gagné !"
"""
    checkpointer = MemorySaver()
    agent = create_agent(
        model=model,
        tools=[],  
        system_prompt=system_prompt,
        checkpointer=checkpointer
    )
    return agent

def play_akinator():
    print("\n" + "=" * 60)
    print("🧞 BIENVENUE DANS AKINATOR 🧞")
    print("=" * 60)
    print("Choisissez une catégorie :")
    print("1. Personnages (réels ou fictifs)")
    print("2. Objets")
    print("3. Animaux")
    print("(Tapez 'quit' pour revenir au menu)")
    
    while True:
        choice = input("\nVotre choix (1/2/3) : ").strip().lower()
        if choice in ['quit', 'exit']:
            return
        elif choice == "1":
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
    
    agent = create_akinator_agent(category)
    # Générer un ID unique pour que la mémoire reparte à zéro à chaque nouvelle partie
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    
    print("\n" + "-" * 40)
    print("LA PARTIE COMMENCE (Tapez 'quit' pour arrêter)")
    print("-" * 40 + "\n")
    
    response = agent.invoke({
        "messages": [HumanMessage(content="Commence le jeu en posant ta première question.")]
    }, config)
    
    agent_message = re.sub(r'<think>.*?</think>', '', response['messages'][-1].content, flags=re.DOTALL).strip()
    print(f"Akinator : {agent_message}\n")
    
    question_count = 1
    
    while True:
        user_input = input("Vous : ").strip()
        
        if user_input.lower() in ['quit', 'quitter', 'exit', 'stop']:
            print("\nFin de la partie Akinator.")
            break
        if not user_input:
            continue
            
        response = agent.invoke({
            "messages": [HumanMessage(content=user_input)]
        }, config)
        
        agent_message = re.sub(r'<think>.*?</think>', '', response['messages'][-1].content, flags=re.DOTALL).strip()
        
        if "j'ai gagné" in agent_message.lower():
            print(f"\nAkinator : {agent_message}")
            print("\n" + "=" * 60)
            print("🎉 PARTIE TERMINÉE : AKINATOR A GAGNÉ ! 🎉")
            print("=" * 60)
            break
            
        question_count += 1
        print(f"\nAkinator : {agent_message}\n")
        
        if question_count > 50:
            print("\nLimite de questions atteinte ! Vous avez battu Akinator.")
            break


# ==========================================
# JEU 2 : BLACK STORIES
# ==========================================
HISTOIRE_SECRETE = """
    Lors d'une soirée alcoolisée au bar réunissant 3 copains, l'un deux, un cambodgien sortit de son sac une mine antipersonnelle vieille de 25 ans qu'il avait déterrée dans son jardin.
    Completement ivres, les hommes décidèrent de mettre leur courage à l'épreuve : à chaque verre, chaque buveur piétinait violemment la mine.
    Les autres clients réussirent à quitter le bar juste avant que le malheur ne survienne : la mine explosa, pulvérisant les trois ivrognes.
    """
SITUATION_PUBLIQUE = """
    Une manipulation maladroite d'un fragment de leur histoire causa la mort de trois hommes.
    """

def bs_analyser_intention(texte_joueur: str) -> str:
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
        temperature=0.1 
    )
    system_prompt = """Tu es un classifieur de texte. 
    - Question courte cherchant un indice -> "QUESTION".
    - Affirmation ou théorie développée -> "SOLUTION".
    Réponds UNIQUEMENT par l'un de ces deux mots."""
    response = model.invoke([SystemMessage(content=system_prompt), HumanMessage(content=texte_joueur)])
    return re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL).strip().upper()

def bs_interroger_narrateur(question: str) -> str:
    log_game(f"\n[Toi, le Détective] Pose la question : {question}")
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
        temperature=0.3
    )
    system_prompt = f"""Tu es le Narrateur d'une partie de Black Stories.
        Histoire secrète : {HISTOIRE_SECRETE}
        Réponds QUE par : "Oui", "Non", "Probablement", "Probablement pas" ou "Pas pertinent"."""
    response = model.invoke([SystemMessage(content=system_prompt), HumanMessage(content=question)])
    rep_propre = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL).strip()
    log_game(f"[Le Narrateur] : {rep_propre}")
    return rep_propre

def bs_proposer_solution_finale(histoire_proposee: str) -> str:
    log_game(f"\n[Toi, le Détective] Propose la solution : {histoire_proposee}")
    arbiter = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
        temperature=0.3
    )
    arbiter_prompt = f"""Tu es l'arbitre intraitable d'une partie de Black Stories.
        VÉRITÉ : {HISTOIRE_SECRETE}
        PROPOSITION : {histoire_proposee}
        Si correct et précis -> réponds EXACTEMENT : "VICTOIRE".
        Sinon -> dis ce qu'il manque en une phrase."""
    response = arbiter.invoke([HumanMessage(content=arbiter_prompt)])
    verdict_propre = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL).strip()
    log_game(f"[L'Arbitre] : {verdict_propre}")
    return verdict_propre

def play_black_stories():
    with open("game.txt", "w", encoding="utf-8") as f:
        f.write("=== LOG DE LA PARTIE ===\n")

    print("\n" + "="*60)
    print("🕵️ BIENVENUE DANS BLACK STORIES 🕵️")
    print("="*60)
    print(f"\nSituation initiale : {SITUATION_PUBLIQUE.strip()}\n")
    print("Tu es le détective ! Pose tes questions directement ou propose ta théorie complète.")
    print("(Tape 'quit' à tout moment pour arrêter)\n")

    while True:
        texte_joueur = input("\n> ").strip()

        if texte_joueur.lower() in ["quitter", "exit", "quit", "stop"]:
            print("\nFin de la partie. L'histoire restera un mystère...")
            break
        if not texte_joueur:
            continue

        intention = bs_analyser_intention(texte_joueur)

        if "SOLUTION" in intention:
            verdict = bs_proposer_solution_finale(texte_joueur)
            if "VICTOIRE" in verdict.upper():
                print("\n🎉 FÉLICITATIONS ! Tu as résolu le mystère ! 🎉")
                break
        else:
            bs_interroger_narrateur(texte_joueur)


# ==========================================
# HUB PRINCIPAL
# ==========================================
def main_menu():
    """Le menu principal du Hub de Jeux"""
    while True:
        print("\n" + "#" * 60)
        print("🎮 HUB DES JEUX IA 🎮".center(60))
        print("#" * 60)
        print("Que voulez-vous faire ?")
        print("  1. Jouer à Akinator (L'IA devine à quoi vous pensez)")
        print("  2. Jouer à Black Stories (Vous devinez l'histoire de l'IA)")
        print("\n(Tapez 'exit' ou 'quit' pour fermer le programme)")
        
        choix = input("\nVotre choix : ").strip().lower()

        if choix in ['quit', 'exit', 'quitter']:
            print("\nMerci d'avoir joué ! À la prochaine ! 👋")
            break
        elif choix == '1':
            play_akinator()
        elif choix == '2':
            play_black_stories()
        else:
            print("\n⚠️ Choix invalide. Veuillez taper 1, 2 ou exit.")

if __name__ == "__main__":
    main_menu()