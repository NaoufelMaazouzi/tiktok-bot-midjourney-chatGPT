import openai
import json

openai.api_key = 'pk-tXDlJKGzANFNEkoyRUBSeJhVLVWUTCqUCgVDUqTbihBtSUve'
openai.api_base = 'https://api.pawan.krd/v1'

def createScript():
    print('Start creating script with chatGPT...')
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": """Racontes moi histoire d’horreur très intrigante et qui fait froid dans le dos, il faut que ce soit le plus réaliste possible, comme une histoire vraie. Tu peux t’inspirer de vraies histoires. L’histoire doit réunir ces thèmes: horreur, lugubre, nuit, peur, terrifiant, épouvante, horrifique, stressant, intrigue, thriller, angoissant, surnaturel, effrayant, histoire, drame, meurtre, épouvante, paranormal, fantastique, tueur. Je vais l'utiliser pour une vidéo tikot donc il faut que l'histoire soit facilement illustrable et qu'elle dure au moins 1min. Après chaque phrase (donc dès qu'il y a un point en fin de phrase), donne moi un prompt Midjourney pour générer une image en rapport avec la phrase. Pas besoin de mettre les verbes "Génère", "Produis" etc pour les prompts et remplace les noms propre pas "un homme" ou "une femme" en fonction du genre du personnage en question. Le début de chaque prompt doit toujours commencer par “Une photo”. Avant le prompt écrit "Prompt:". Voilà un exemple de ce que j’attends: “{“Text”: “Vous ne croirez jamais ce qu’il s’est passé pour Forrest Fenn.”,
“Text”: “Il y a quelques années, un homme du nom de Forrest Fenn a caché un trésor d'une valeur de plus de 2 millions de dollars quelque part dans les montagnes Rocheuses.”,
“Prompt”: “Une photo d’une vue de montagnes rocheuses dans l'horizon”,
“Text”: “Les indices pour trouver le trésor sont cachés dans un poème qu'il a écrit et publié dans son livre "The Thrill of the Chase",
“Prompt”: “Une photo d’un livre ouvert avec des poèmes”,
“Text”: “Depuis lors, des milliers de personnes ont tenté de trouver le trésor en utilisant les indices du poème.”,
“Prompt”: “Une photo d’un groupe de chasseurs de trésors qui planifient leur expédition” }”
Tu dois ajouter beaucoup de détails dans les prompts pour donner une ambiance horreur et lugubre. La première phrase de l’histoire doit être comme celles-là: “Vous ne croirez jamais ce qu’il s’est passé”, “Je n’arrive pas à croire que personne ne parle de cela”. Les prompts doivent décrire comme celà: “Une photo de l’extérieur d’une maison maintenant abandonnée” et non pas “Une photo de l’extérieur de la maison maintenant abandonnée”. Retourne moi l’histoire sous le format d’un tableau contenant un seul objet avec “text” en clé pour l’histoire et la clé “Prompt” pour les prompts. Voilà un exemple: [{“Text”: “Vous ne croirez jamais ce qu’il s’est passé pour Forrest Fenn.”,
“Text”: “Il y a quelques années, un homme du nom de Forrest Fenn a caché un trésor d'une valeur de plus de 2 millions de dollars quelque part dans les montagnes Rocheuses.”,
“Prompt”: “Une photo d’une vue de montagnes rocheuses dans l'horizon”,
“Text”: “Les indices pour trouver le trésor sont cachés dans un poème qu'il a écrit et publié dans son livre "The Thrill of the Chase",
“Prompt”: “Une photo d’un livre ouvert avec des poèmes”,
“Text”: “Depuis lors, des milliers de personnes ont tenté de trouver le trésor en utilisant les indices du poème.”,
“Prompt”: “Une photo d’un groupe de chasseurs de trésors qui planifient leur expédition” }]
"""}
    ]
    )

    script = completion.choices[0].message.content
    if script and type(script) == str:
        print(script)
        script_array = json.loads(script)
        with open('prompts.txt', 'w', encoding='utf-8') as f:
            for objet in script_array:
                prompt = f"{objet['Prompt']}, horreur, lugubre, nuit, peur, terrifiant, épouvante, horrifique, stressant, intrigue, thriller, angoissant, surnaturel, effrayant, histoire, drame, meurtre, épouvante, paranormal, fantastique, tueur, Netflix, 8K --v 5 --q 2 --ar 9:16"
                f.write(prompt + '\n')
        with open('script.txt', 'w', encoding='utf-8') as f:
            for objet in script_array:
                text = objet['Text']
                f.write(text + '\n')
        print('Script finished...')
    else:
        print('Script failed')
        return
    return script_array

