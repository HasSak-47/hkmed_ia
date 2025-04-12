import sqlite3
import pandas
import requests

def add_ingredient(ui, name, cursor: sqlite3.Cursor):
    cursor.execute("""
    INSERT INTO ingredient (ingredient_rxcui, ingredient_name)
    VALUES (?, ?)
    """, (ui, name))

    return cursor.lastrowid

def add_effect(meddra_id, meddra_term, cursor: sqlite3.Cursor):
    cursor.execute("""
    INSERT INTO adverse_effect (pt_meddra_id, pt_meddra_term)
    VALUES (?, ?)
    """, (meddra_id, meddra_term))

    return cursor.lastrowid

def add_interaction(effect_id, notes, cursor: sqlite3.Cursor):
    cursor.execute("""
    INSERT INTO interaction (effect_id, notes)
    VALUES (?, ?)
    """, (effect_id, notes))

    return cursor.lastrowid

def add_interaction_ingredient(interaction_id, ingredient_id, cursor: sqlite3.Cursor):
    cursor.execute("""
    INSERT INTO interaction_ingredients (interaction_id, ingredient_id)
    VALUES (?, ?)
    """, (interaction_id, ingredient_id))

def add_condition(name, cursor: sqlite3.Cursor):
    cursor.execute("""
    INSERT INTO condition (name) VALUES (?)
    """, (name,))

    return cursor.lastrowid

def add_treatment(ing_id, c_id, cursor: sqlite3.Cursor):
    cursor.execute("""
    INSERT INTO treatment (condition_id, ingredient_id)
    VALUES (?, ?)
    """, (ing_id, c_id))

    return cursor.lastrowid

def load_nsides(db: sqlite3.Connection):
    df = pandas.read_csv(f'nsides/20240925/adverse_reactions.csv', sep=",")
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingredient (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient_rxcui TEXT,
        ingredient_name TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS adverse_effect (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pt_meddra_id INTEGER,
        pt_meddra_term TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interaction (
        id INTEGER PRIMARY KEY,
        effect_id INTEGER NOT NULL,
        notes TEXT,
        FOREIGN KEY (effect_id) REFERENCES adverse_effect(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE interaction_ingredients (
        interaction_id INTEGER NOT NULL,
        ingredient_id INTEGER NOT NULL,
        FOREIGN KEY (interaction_id) REFERENCES interaction(id),
        FOREIGN KEY (ingredient_id) REFERENCES ingredient(id),
        PRIMARY KEY (interaction_id, ingredient_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS condition (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS treatment (
        condition_id INTEGER NOT NULL,
        ingredient_id INTEGER NOT NULL,
        FOREIGN KEY (condition_id) REFERENCES condition(id),
        FOREIGN KEY (ingredient_id) REFERENCES ingredient(id),
        PRIMARY KEY (condition_id, ingredient_id)
    )
    """)

    ingredients_map = {}
    effects_map = {}
    for _, row in df.iterrows():
        ing_id = (row['ingredients_rxcuis'], row['ingredients_names'])
        # arr of ids of ingredients
        act_ing = []

        # adds ingredients
        if  row['num_ingredients'] == 1:
            if ing_id not in ingredients_map:
                ingredients_map[ing_id] = add_ingredient(row['ingredients_rxcuis'], row['ingredients_names'], cursor)
            act_ing = [ingredients_map[ing_id]]
        else:
            rxcuis= str(row['ingredients_rxcuis']).split(',')
            names = str(row['ingredients_names']).split(',')
            for rxcui, name in zip(rxcuis, names):
                rxcui = rxcui.replace(' ', '')
                name = name.replace(' ', '')
                if rxcui not in ingredients_map:
                    ingredients_map[rxcui] = add_ingredient(rxcui, name, cursor)
                act_ing.append(ingredients_map[rxcui])

            pass

        # add adverse effects
        eff_id = row['pt_meddra_id']
        if eff_id not in effects_map:
            effects_map[eff_id] = add_effect(row['pt_meddra_id'], row['pt_meddra_term'], cursor)

        # add interaction
        interaction_id = add_interaction(effects_map[eff_id], '', cursor)
        # add interaction, ingredient relation
        for ingredient in act_ing:
            add_interaction_ingredient(interaction_id, ingredient, cursor)


    get_uses(cursor)


    cursor.close()
    db.commit()
    pass

def get_uses(cursor: sqlite3.Cursor):
    cursor.execute("SELECT id, ingredient_rxcui FROM ingredient")
    rows = cursor.fetchall()

    conditions = {}
    treatments = set()
    tt = len(rows)
    for i, row in enumerate(rows):
        print(f'{100 * i / tt:0.3}%')
        ing_id = row[0]
        rxcui = row[1]
        url = f'https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json'
        params = {
            'rxcui': rxcui,
            'rela': 'may_treat',
            'relaSource': 'MEDRT'
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            continue

        data = response.json()
        info_list = data.get("rxclassDrugInfoList", {}).get("rxclassDrugInfo", [])
        
        if not info_list:
            continue

        for entry in info_list:
            condition = entry["rxclassMinConceptItem"]["className"]
            if condition not in conditions:
                conditions[condition] = add_condition(condition, cursor)

            if (ing_id, conditions[condition]) not in treatments:
                add_treatment(ing_id, conditions[condition], cursor)
                treatments.add((ing_id, conditions[condition]))

    pass

def print_db(db: sqlite3.Connection):
    cursor = db.cursor()
    tables = ['ingredient', 'adverse_effect', 'interaction', 'interaction_ingredients', 'condition', 'treatment']
    for table in tables:
        print(f"Rows for table {table}:")
        
        # Execute SELECT statement to fetch all rows from the table
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        # Print the rows
        for row in rows:
            print(row)
        
        print("\n" + "="*40 + "\n")

def main():
    db = sqlite3.connect('meds.db')
    from sys import argv
    if len(argv) == 1:
        db.close()
        return
    if argv[1] == 'nsides':
        load_nsides(db)
    elif argv[1] == 'print_db':
        print_db(db)

    db.close()

if __name__ == "__main__":
    main()
