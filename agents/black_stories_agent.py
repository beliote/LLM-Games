import os
import re
import json
import random
import uuid
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

def log_game(message):
    """Affiche dans la console ET écrit dans game.txt"""
    print(message)  
    with open("game.txt", "a", encoding="utf-8") as f:
        f.write(str(message) + "\n")

def charger_histoire_aleatoire(chemin_fichier="data/stories.json"):
    """Lit le fichier JSON et retourne une histoire au hasard."""
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            histoires = json.load(f)
        return random.choice(histoires)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {chemin_fichier} est introuvable.")
        return {
            "situation": "Une erreur informatique a causé la fin du jeu.",
            "histoire": "Le développeur a oublié de créer le fichier stories.json."
        }


# ==========================================
# CRÉATION DE L'AGENT MAÎTRE DU JEU
# ==========================================
def create_black_stories_agent(histoire_secrete: str, situation: str):
    """
    Crée l'agent principal. On définit l'outil "verifier_solution" à l'intérieur 
    pour qu'il ait accès aux variables de l'histoire en cours.
    """

    # --- L'OUTIL DE L'AGENT ---
    @tool
    def verifier_solution(proposition: str) -> str:
        """
        OUTIL OBLIGATOIRE : À utiliser UNIQUEMENT lorsque le joueur propose une théorie longue,
        une explication complexe ou la solution finale de l'histoire.
        """
        arbiter = ChatOpenAI(
            model=os.getenv("AI_MODEL"),
            base_url=os.getenv("AI_ENDPOINT"),
            api_key=os.getenv("AI_API_KEY"),
            temperature=0.1
        )
        arbiter_prompt = f"""Tu es l'arbitre intraitable d'une partie de Black Stories.
            SITUATION : {situation}
            VÉRITÉ : {histoire_secrete}
            PROPOSITION : {proposition}

            MISSION :
            Si la solution est globalement correcte (cause, objet, contexte), réponds EXACTEMENT : "VICTOIRE".
            Sinon, dis-lui ce qu'il manque en une phrase courte sans donner la réponse."""
        
        response = arbiter.invoke([HumanMessage(content=arbiter_prompt)])
        return re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL).strip()


    # --- MODÈLE ET L'AGENT ---
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
        temperature=0.3
    )

    system_prompt = f"""Tu es le Maître du Jeu d'une partie de Black Stories. Le joueur est le détective.
    
    SITUATION INITIALE : {situation}
    VÉRITABLE HISTOIRE : {histoire_secrete}

    RÈGLES DE COMPORTEMENT :
    1. Si le joueur te pose une QUESTION FERMÉE (pour avoir un indice) : 
       -> N'utilise AUCUN outil. Réponds TOI-MÊME en utilisant STRICTEMENT ET UNIQUEMENT l'une de ces réponses : "Oui", "Non", "Probablement", "Probablement pas" ou "Pas pertinent". Ne dis absolument rien d'autre.
    
    2. Si le joueur PROPOSE UNE SOLUTION (théorie complexe, "je pense que...", etc.) :
       -> Tu DOIS obligatoirement utiliser l'outil 'verifier_solution' avec la proposition du joueur.
       -> Si l'outil te répond "VICTOIRE", annonce au joueur qu'il a gagné et raconte-lui l'histoire complète avec enthousiasme.
       -> Si l'outil te répond autre chose, répète la réponse de l'outil au joueur pour le guider.
    """

    checkpointer = MemorySaver()
    
    agent = create_agent(
        model=model,
        tools=[verifier_solution], 
        system_prompt=system_prompt,
        checkpointer=checkpointer
    )
    
    return agent


# ==========================================
# BOUCLE DE JEU
# ==========================================
def play_black_stories():
    histoire_actuelle = charger_histoire_aleatoire()
    SITUATION_PUBLIQUE = histoire_actuelle["situation"]
    HISTOIRE_SECRETE = histoire_actuelle["histoire"]
    TITRE = histoire_actuelle.get("titre", "Mystère")

    agent = create_black_stories_agent(HISTOIRE_SECRETE, SITUATION_PUBLIQUE)
    
    config = {"configurable": {"thread_id": "bs_game"}}

    print("\n" + "=" * 60)
    print("=== DÉBUT DE LA PARTIE DE BLACK STORIES ===")
    print("=" * 60)
    print(f"\nSituation initiale : {SITUATION_PUBLIQUE.strip()}\n")
    print("Tu es le détective ! Pose tes questions fermées ou propose ta théorie complète.")
    print("(Tape 'quitter' à tout moment pour arrêter)\n")

    while True:
        user_input = input("\n> ").strip()

        if not user_input:
            continue
            
        if user_input.lower() in ["quitter", "exit", "quit", "stop"]:
            print(f"\nFin de la partie. La vérité (Titre: {TITRE}) était :\n{HISTOIRE_SECRETE}")
            return False 

        response = agent.invoke({
            "messages": [HumanMessage(content=user_input)]
        }, config)

        # Récupération et nettoyage de la réponse
        agent_message_brut = response['messages'][-1].content
        agent_message = re.sub(r'<think>.*?</think>', '', agent_message_brut, flags=re.DOTALL).strip()
        
        log_game(f"[Toi] {user_input}")
        log_game(f"[Maître du Jeu] {agent_message}")

        if "victoire" in agent_message.lower() or "gagné" in agent_message.lower() or "félicitations" in agent_message.lower():
            print("\nFÉLICITATIONS ! Tu as résolu le mystère !")
            
            print("\n" + "=" * 60)
            rejouer = input("\nVoulez-vous enquêter sur une autre histoire ? (oui/non) : ").strip().lower()
            if rejouer in ['oui', 'o', 'yes', 'y']:
                print("\n" * 2)
                return True # On renvoie True au Hub pour qu'il relance la fonction
            
            return False # On renvoie False pour dire qu'on arrête


if __name__ == "__main__":
    play_black_stories()