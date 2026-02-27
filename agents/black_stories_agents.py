import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

def create_narrator_agent(histoire_secrete: str):
    """
    Crée l'agent Narrateur pour Black Stories.
    Il connaît l'histoire mais ne peut répondre que par Oui, Non, ou Pas pertinent.
    """
    
    # Modèle 
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
        temperature=0.1
    )

    # Prompt pour que le narrateur ne réponde que par oui ou non
    system_prompt = f"""Tu es le Maître du Jeu (Narrateur) d'une partie de Black Stories.
        Voici l'histoire complète et secrète que le détective doit deviner :
        ---
        {histoire_secrete}
        ---

        RÈGLES ABSOLUES :
        1. Le détective va te poser des questions.
        2. Tu ne dois répondre QUE par l'une de ces trois options, sans AUCUN autre mot ni ponctuation supplémentaire :
        - "Oui" (si la réponse est correcte selon l'histoire secrète)
        - "Non" (si la réponse est fausse selon l'histoire secrète)
        - "Pas pertinent" (si la question n'a pas d'importance pour résoudre l'énigme)
        3. Ne justifie jamais tes réponses. Ne donne aucun indice. Ne fais pas de phrases.
        """

    # Création de l'agent 
    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=system_prompt,
    )
    
    return agent


# TEST
if __name__ == "__main__":

    histoire_test = """
        ENONCE : Un homme rentre dans un bar et demande un verre d'eau. Le barman sort un pistolet et le braque sur lui. L'homme dit 'Merci' et s'en va. 
        ---
        EXPLICATION : l'homme avait le hoquet, le barman l'a guéri en lui faisant peur)."""
    
    narrateur = create_narrator_agent(histoire_test)
    
    question = "Est-ce que l'homme avait soif ?"
    print(f"Détective : {question}")
    
    response = narrateur.invoke({
        "messages": [HumanMessage(content=question)]
    })
    
    print(f"Narrateur : {response['messages'][-1].content}")