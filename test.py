from collections import defaultdict
import sqlite3
from time import sleep
from sentence_transformers import SentenceTransformer, util
from pprint import pprint

model = SentenceTransformer('ls-da3m0ns/bge_large_medical')

def enconde_deathliness(cur: sqlite3.Cursor):
    cur.execute("SELECT * FROM adverse_effect")

    death_encode = model.encode("death")

    for i in cur.fetchall():
        # a = " ".join(i[2].split(" ")[:-1])
        # print(a)
        a_encode = model.encode(i[2])

        score = util.dot_score(death_encode, a_encode)[0][0].item()

        cur.execute(f"""
            UPDATE 'adverse_effect'
            SET deathliness_score = {score}
            WHERE
                id = {i[0]}
        """)
    pass


# symptoms = ['Diabetic Nephropathies']
symptoms = []

from thefuzz import fuzz

def get_symptoms(cur: sqlite3.Cursor):
    symptom = ""


    symptoms = []
    for symp in cur.execute('SELECT * from condition').fetchall():
        symptoms.append(symp)

    while symptom != "NA":
        symptom = input("Input a new symptom, NA to end ")
        if symptom in symptoms:
            symptoms.append(symptom)

        # guess
        candidates = []
        for symp in symptoms:
            ratio = fuzz.ratio(symptom, symp)
            candidates.append((symp, ratio))

        candidates.sort(key=lambda x: x[1])
        found = False
        for can, ratio in candidates:
            if ratio < .2:
                break

            if input(f'did you mean {can} y?') == 'y':
                found = True
                symptom = can

        if not found:
            print('try again')
            continue

        if symptom != "NA":
            symptoms.append(symptom)

def get_treatment_ids(cur, symptom):
    filt = cur.execute(f"""
        SELECT condition_id, treatment.ingredient_id, name, ingredient_name, interaction_id, deathliness_score FROM treatment 
        JOIN condition ON condition.id = condition_id
        JOIN 'ingredient' ON ingredient.id = treatment.ingredient_id
        JOIN interaction_ingredients ON interaction_ingredients.ingredient_id = ingredient.id
        JOIN interaction ON interaction.id = interaction_ingredients.interaction_id
        JOIN adverse_effect ON adverse_effect.id = effect_id
        WHERE name IN (?)
    """, (symptom,)).fetchall()

    meds = defaultdict(lambda : 0)
    for c_id, ing_id, name, ing_n, int_id, score in filt:
        meds[ing_n] += score

    return meds



def get_random_conditions(cursor: sqlite3.Cursor):
    cursor.execute("""
        SELECT name 
        FROM condition
        LIMIT 3;
    """)
    return [row[0] for row in cursor.fetchall()]


def get_random_ingridents(cursor: sqlite3.Cursor):
    data =  cursor.execute("""
        SELECT id, ingredient_name
        FROM ingredient
        LIMIT 10;
    """).fetchall()
    return (
            [row[0] for row in data],
            [row[1] for row in data])

def get_effects(ingredient_ids, db: sqlite3.Connection):
    if not ingredient_ids:
        return []

    placeholders = ",".join("?" for _ in ingredient_ids)
    
    query = f"""
    SELECT DISTINCT i.id AS interaction_id,
                    ae.pt_meddra_id,
                    ae.pt_meddra_term,
                    ae.deathliness_score
    FROM interaction i
    JOIN interaction_ingredients ii ON i.id = ii.interaction_id
    JOIN adverse_effect ae ON i.effect_id = ae.id
    WHERE ii.ingredient_id IN ({placeholders})
    """
    cursor = db.cursor()
    cursor.execute(query, ingredient_ids)
    interactions = cursor.fetchall()

    # Now filter the interactions to exclude those involving ingredients not in the list
    filtered_interactions = []

    for interaction in interactions:
        interaction_id = interaction[0]
        
        # Check which ingredients are involved in this interaction
        cursor.execute("""
        SELECT ii.ingredient_id
        FROM interaction_ingredients ii
        WHERE ii.interaction_id = ?
        """, (interaction_id,))
        
        involved_ingredients = [row[0] for row in cursor.fetchall()]
        
        # Check if all involved ingredients are in the provided list
        if all(ingredient in ingredient_ids for ingredient in involved_ingredients):
            filtered_interactions.append(interaction)

    return filtered_interactions

def main():
    db = sqlite3.connect('meds_weighted.db')
    cur = db.cursor()

    (ids, names) = get_random_ingridents(cur)
    print('testing the following ingredients:')
    for name in names:
        arint(name, ', ', end='')

    effects = get_effects(ids, db)
    print('warning! using this ingredients may cause the next adverse effects')
    for effect in effects:
        print(f'"{effect[2]}" which it has a deathliness score of "{effect[3]}"')


    db.commit()
    db.close()

if __name__ == "__main__":
    main()
