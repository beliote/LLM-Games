import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from akinator_agent import play_akinator
from black_stories_agent import play_black_stories

load_dotenv()

# ----- DETECTER JEU -----
def detecter_jeu(texte_joueur: str) -> str:
    """
    Utilise le LLM pour déterminer à quel jeu l'utilisateur veut jouer.
    Retourne "AKINATOR", "BLACK_STORIES", "QUITTER", ou "INCONNU".
    """
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
        temperature=0.0 # Température à 0 pour être très strict
    )

    system_prompt = """Tu es l'assistant d'accueil d'un hub de jeux vidéo. 
    L'utilisateur va te dire ce qu'il a envie de faire.
    
    Tu as le choix entre 4 réponses EXACTES, ne dis RIEN d'autre :
    - "AKINATOR" : S'il veut jouer à un jeu de devinettes, faire deviner un mot, un personnage, un objet, ou s'il mentionne explicitement Akinator.
    - "BLACK_STORIES" : S'il veut résoudre une énigme macabre, deviner une histoire, mener une enquête, ou s'il mentionne Black Stories.
    - "QUITTER" : S'il dit au revoir, quitter, exit, stop, etc.
    - "INCONNU" : S'il dit n'importe quoi d'autre qui ne correspond pas aux deux jeux.
    """

    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=texte_joueur)
    ])
    
    # Nettoyage pour certains modèles Groq
    intention = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL).strip().upper()

    if "AKINATOR" in intention: return "AKINATOR"
    if "BLACK_STORIES" in intention: return "BLACK_STORIES"
    if "QUITTER" in intention: return "QUITTER"
    
    return "INCONNU"

# ==========================================
# HUB PRINCIPAL
# ==========================================
def main_menu():
    """Le menu principal intelligent du Hub de Jeux"""
    print("\n" + "-" * 60)
    print("JEUX DISPONIBLES".center(60))
    print("-" * 60)
    print("Bienvenue ! Vous avez le choix entre les jeux suivants :")
    print("- Akinator : Vous pensez à quelque chose, j'essaie de le deviner.")
    print("- Black Stories : Vous menez l'enquête pour deviner mon histoire macabre.")
    
    while True:
        print("\n" + "-"*60)
        choix_texte = input("\nÀ quoi voulez-vous jouer aujourd'hui ? (ou 'quitter') : ").strip()

        if not choix_texte:
            continue

        print("Laissez-moi réfléchir...")
        intention = detecter_jeu(choix_texte)

        if intention == "QUITTER":
            print("\nMerci d'avoir joué !")
            break
            
        elif intention == "AKINATOR":
            print("\nTrès bien, jouons à Akinator !")
            rejouer = True
            while rejouer:
                # True si le joueur veut refaire une partie
                rejouer = play_akinator()
            print("\nRetour au Hub Principal.")
            
        elif intention == "BLACK_STORIES":
            print("\nC'est parti pour une enquête macabre !")
            rejouer = True
            while rejouer:
                play_black_stories()
                # Option rejouer
                rep = input("\nVoulez-vous enquêter sur une autre histoire ? (oui/non) : ").strip().lower()
                rejouer = rep in ['oui', 'o', 'yes', 'y']
            print("\nRetour au Hub Principal.")
            
        else:
            print("\nJe n'ai pas bien compris. Pouvez-vous préciser si vous voulez jouer à 'Akinator', à 'Black Stories', ou 'quitter' ?")

if __name__ == "__main__":
    main_menu()