import os
import re
import json
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

with open("game.txt", "w", encoding="utf-8") as f:
    f.write("=== LOG DE LA PARTIE ===\n")

def log_game(message):
    """Affiche dans la console ET écrit dans game.txt"""
    print(message)  
    with open("game.txt", "a", encoding="utf-8") as f:
        f.write(str(message) + "\n")


# ----- Charger une histoire -----
def charger_histoire_aleatoire(chemin_fichier="C:\\Users\\eliot\\OneDrive\\Documents\\IMT\\LLM\\Projet\\LLM-Games\\data\\stories.json"):
    """Lit le fichier JSON et retourne une histoire au hasard."""
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            histoires = json.load(f)
        return random.choice(histoires)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {chemin_fichier} est introuvable.")
        # On retourne une histoire par défaut si le fichier plante
        return {
            "situation": "Une erreur informatique a causé la fin du jeu.",
            "histoire": "Le développeur a oublié de créer le fichier stories.json."
        }

# ----- CLASSIFICATEURS D'INTENTION -----
# Si le détective cherche à poser une question ou s'il propose une solution complète
def analyser_intention(texte_joueur: str) -> str:
    """
    Détermine si le joueur pose une question ou propose la solution finale.
    """
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
        temperature=0.1 # Température basse pour être déterministe
    )

    system_prompt = """Tu es un classifieur de texte. Ton rôle est d'analyser la phrase d'un joueur qui joue au détective.
    RÈGLES :
    - Si la phrase est une question courte cherchant à obtenir un indice (ex: "Étaient-ils amis ?", "L'objet était-il une arme ?"), réponds STRICTEMENT ET UNIQUEMENT par le mot : "QUESTION".
    - Si la phrase est une affirmation, une théorie développée ou commence par des mots comme "Je pense que...", "L'histoire est...", réponds STRICTEMENT ET UNIQUEMENT par le mot : "SOLUTION".
    Ne dis rien d'autre.
    """

    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=texte_joueur)
    ])
    
    # Nettoyage pour certains modèles Groq
    intention = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL).strip().upper()
    return intention

# ----- NARRATEUR -----
def interroger_narrateur(question: str, histoire_secrete: str) -> str:
    log_game(f"\n[Toi, le Détective] Pose la question : {question}")

    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
        temperature=0.3
    )

    # Prompt Narrateur
    system_prompt = f"""Tu es le Maître du Jeu (Narrateur) d'une partie de Black Stories.
        Voici l'histoire secrète :
        ---
        {histoire_secrete}
        ---
        RÈGLES ABSOLUES :
        Tu ne dois répondre QUE par : "Oui", "Non", "Probablement", "Probablement pas" ou "Pas pertinent".
        Aucun autre mot. Aucune ponctuation.
        """

    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ])
    
    # Nettoyage pour certains modèles Groq
    response_propre = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL).strip()

    log_game(f"[Le Narrateur] : {response_propre}")
    return response_propre
    

# --- ARBITRE DE LA SOLUTION ---
def proposer_solution_finale(histoire_proposee: str, histoire_secrete: str, situation: str) -> str:
    log_game(f"\n[Toi, le Détective] Propose la solution : {histoire_proposee}")
    
    arbiter = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
        temperature=0.3
    )

    # Prompt Arbitre
    arbiter_prompt = f"""Tu es l'arbitre intraitable d'une partie de Black Stories.
        SITUATION : {situation}
        VÉRITÉ : {histoire_secrete}
        PROPOSITION : {histoire_proposee}

        MISSION :
        Si la solution est globalement correcte et précise sur la cause, l'objet et le contexte, réponds EXACTEMENT : "VICTOIRE".
        Sinon, dis-lui ce qu'il manque en une phrase courte sans donner la réponse.
        """
    
    response = arbiter.invoke([HumanMessage(content=arbiter_prompt)])
    verdict = response.content

    # Nettoyage pour certains modèles Groq
    verdict_propre = re.sub(r'<think>.*?</think>', '', verdict, flags=re.DOTALL).strip()

    log_game(f"[L'Arbitre] : {verdict_propre}")
    return verdict_propre


# ----- PARTIE -----
def play_black_stories():

    # Histoire au hasard
    histoire_actuelle = charger_histoire_aleatoire()
    SITUATION_PUBLIQUE = histoire_actuelle["situation"]
    HISTOIRE_SECRETE = histoire_actuelle["histoire"]
    TITRE = histoire_actuelle.get("titre", "Mystère")

    print("\n" + "-"*50)
    print("=== DÉBUT DE LA PARTIE DE BLACK STORIES ===")
    print("-"*50)
    print(f"\nSituation initiale : {SITUATION_PUBLIQUE.strip()}\n")
    print("Tu es le détective ! Pose tes questions directement ou propose ta théorie complète.")
    print("(Tape 'quitter' à tout moment pour arrêter)\n")

    while True:
        texte_joueur = input("\n> ").strip()

        if texte_joueur.lower() in ["quitter", "exit", "quit", "stop"]:
            print("\nFin de la partie. L'histoire restera un mystère...")
            break
            
        if not texte_joueur:
            continue

        intention = analyser_intention(texte_joueur)

        if "SOLUTION" in intention:
            verdict = proposer_solution_finale(texte_joueur, HISTOIRE_SECRETE, SITUATION_PUBLIQUE)
            if "VICTOIRE" in verdict.upper():
                print("\nFÉLICITATIONS ! Tu as résolu le mystère !")
                break
        else:
            interroger_narrateur(texte_joueur, HISTOIRE_SECRETE)


if __name__ == "__main__":
    play_black_stories()