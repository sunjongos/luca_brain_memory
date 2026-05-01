from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'neo4j'))
with driver.session(database='system') as session:
    session.run("ALTER CURRENT USER SET PASSWORD FROM 'neo4j' TO 'password'")
print("Password changed successfully!")
