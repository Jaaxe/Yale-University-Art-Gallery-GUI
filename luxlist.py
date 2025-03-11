import argparse
import sqlite3
import shutil
import table as t



def create_table(data):
    print(f"Search produced {len(data)} objects.")

    headers = ["ID", "Label", "Date", "Produced By", "Classified As"]

    table = t.Table(headers, data)  # 'w' for wrapped, 't' for truncated

    print(table)

def query_database(cursor, date, agt, cls, label):
    #base query
    query = """
    SELECT 
        o.id, 
        o.label, 
        o.date, 
        (
            SELECT GROUP_CONCAT(DISTINCT agent_part)
            FROM (
                SELECT a.name || ' (' || p.part || ')' AS agent_part
                FROM productions p
                JOIN agents a ON p.agt_id = a.id
                WHERE p.obj_id = o.id
                ORDER BY a.name ASC, p.part ASC
            )
        ) AS sorted_agents,
        (
            SELECT GROUP_CONCAT(DISTINCT cls_name)
            FROM (
                SELECT c.name AS cls_name
                FROM objects_classifiers oc
                JOIN classifiers c ON oc.cls_id = c.id
                WHERE oc.obj_id = o.id
                ORDER BY c.name ASC
            )
        ) AS ordered_classifiers

    FROM objects o
        LEFT JOIN productions p ON p.obj_id == o.id
        LEFT JOIN agents a ON a.id == p.agt_id
        LEFT JOIN objects_classifiers oc ON o.id == oc.obj_id
        LEFT JOIN classifiers c ON c.id == oc.cls_id
        WHERE 1=1
    """
    params = []

    #conditionals to add onto base query
    if date:
        query += " AND o.date LIKE ?"
        params.append(f"%{date}%")
    if agt:
        query += " AND a.name LIKE ?"
        params.append(f"%{agt}%")
    if cls:
        query += " AND c.name LIKE ?"
        params.append(f"%{cls}%")
    if label:
        query += " AND o.label LIKE ?"
        params.append(f"%{label}%")

    query += """
    GROUP BY o.id
    ORDER BY o.label ASC, o.date ASC
    LIMIT 1000
    """

    cursor.execute(query, params)
    
    results = cursor.fetchall()

    return results
   



def cli_parser():
    parser = argparse.ArgumentParser(
        prog= "lux.py",
        allow_abbrev=False,
    )
    
    parser.add_argument("-d", metavar="date", help="show only those objects whose date contains date")
    parser.add_argument("-a", metavar="agt", help="show only those objects produced by an agent with name containing agt")
    parser.add_argument("-c", metavar="cls", help="show only those objects classified with a classifier having a name containing cls")
    parser.add_argument("-l", metavar="label", help="show only those objects whose label contains label")
    
    args = parser.parse_args()

    return args


def main():
    #put this in main to create only one instance
    conn = sqlite3.connect("lux.sqlite")
    cursor = conn.cursor()

    args = cli_parser()
    results = query_database(cursor, args.d, args.a, args.c, args.l)
    create_table(results)

    #closes connection
    conn.close()

if __name__ == "__main__":
    main()