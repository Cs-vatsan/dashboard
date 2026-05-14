from db import *

init_db()

employees = [

    (
        "John Doe",
        "Engineering",
        "john@company.com",
        "Developer"
    ),

    (
        "Jane Smith",
        "HR",
        "jane@company.com",
        "HR Manager"
    ),

    (
        "Mike Ross",
        "Sales",
        "mike@company.com",
        "Sales Lead"
    ),
]

for emp in employees:

    try:
        add_employee(*emp)

    except:
        pass

print("Seed data inserted successfully.")