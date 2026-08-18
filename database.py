import sqlite3
import random


connection = sqlite3.connect("members.db")

cursor = connection.cursor()



cursor.execute("""
CREATE TABLE IF NOT EXISTS members (

id INTEGER PRIMARY KEY AUTOINCREMENT,

rank INTEGER,

name TEXT,

member_id TEXT,

code TEXT,

level TEXT,

income TEXT,

withdrawal TEXT,

payment TEXT,

tasks TEXT,

status TEXT,

photo TEXT

)
""")


cursor.execute(
"DELETE FROM members"
)



levels = [

"VIP Member",
"VVIP Member",
"Silver Member",
"Gold Member",
"Diamond Member",
"Platinum Member",
"Ruby Global Member"

]


for i in range(1,101):


    level = random.choice(levels)


    cursor.execute("""

    INSERT INTO members

    (
    rank,
    name,
    member_id,
    code,
    level,
    income,
    withdrawal,
    payment,
    tasks,
    status,
    photo
    )

    VALUES (?,?,?,?,?,?,?,?,?,?,?)

    """,

    (

    i,

    f"VIP Member {i}",

    f"MEM{i:03}",

    f"VIP-{random.randint(1000,9999)}",

    level,

    f"${random.randint(1000,50000):,}",

    f"${random.randint(500,30000):,}",

    "Completed",

    f"{random.randint(80,100)}%",

    "Active",

    "gold.png"

    ))



connection.commit()

connection.close()


print("VIP Final Database Created Successfully")