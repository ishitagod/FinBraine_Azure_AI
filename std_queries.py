import os
STANDARD_QUERIES={
    "questions" : [
        # "Creditvision Score",
        # "Income Tax ID Number (PAN)",
        # "CKYC",
        # "TELEPHONE(s) Section - Telephone Type and Telephone Number",
        # "Consumer",
        # "Date",
        # "Email Contacts",
        # "Addresses - Category, Address",
        # "Summary Accounts - Account Type, Accounts, Advances, Balances, Date Opened",
        # "Enquiries - Enquiry Purpose, Total, Past 30 days, Past 12 months, Past 24 months, Recent",
        # "Accounts (Section) - Account, Dates, Amount, Status, DAYS PAST DUE/ASSET CLASSIFICATION (UP TO 36 MONTHS; LEFT TO RIGHT)",
            # 1. Single numeric field (Creditvision Score)
         "What is the Consumer name?",
         "What is the Creditvision Score? (Answer with the integer value only.)",
 
        # # 2. Single alphanumeric ID (PAN)
         "Income Tax ID Number (PAN)",

        # # 3. CKYC identifier
        "CKYC number",

        # 4. Telephone entries (potentially multiple)
        "List all telephone entries in the form 'Telephone Type:, Telephone Number:', one per line.",

        # 5. Consumer segment/type
        "What is the Consumer type? (E.g., 'Retail', 'Corporate'. Return text only.)",

        # 6. Date of report
        "What is the report Date? (Return in YYYY-MM-DD format.)",

        # 7. Email contacts
        "List all email addresses found under 'Email Contact(s)'",

        # 8. Addresses (with category)
        "List each Address as 'Category: [full address]', one per line.",

        # 9–12. Summary Accounts: break into four separate fields
        "Under 'Summary Accounts', what is the Account Type? (Return text only.)",
        "Under 'Summary Accounts', how many Accounts? (Return the integer count.)",
        "Under 'Summary Accounts', what are the Advances? (Return the numeric total, numbers only.)",
        "Under 'Summary Accounts', what are the Balances? (Return the numeric total, numbers only.)",
        "Under 'Summary Accounts', what is the Date Opened? (Return in YYYY-MM-DD format.)",

        # 13–16. Enquiries: split out each timeframe
        "Under 'Enquiries', what is the Total enquiries? (Return integer only.)",
        "Under 'Enquiries', how many enquiries in the Past 30 days? (Integer only.)",
        "Under 'Enquiries', how many enquiries in the Past 12 months? (Integer only.)",
        "Under 'Enquiries', how many enquiries in the Past 24 months? (Integer only.)",

        # 17. Most recent enquiry purpose
        "What is the Latest Enquiry Purpose? (Return the text of the most recent enquiry.)",

        # 18–22. Accounts (Section) – again, split into clear sub‑questions
        "Under 'Accounts (Section)', list each Account name, one per line.",
        "Under 'Accounts (Section)', list each Date (for each account), one per line (YYYY-MM-DD).",
        "Under 'Accounts (Section)', list each Amount, one per line (numbers only).",
        "Under 'Accounts (Section)', list each Status, one per line.",
        "Under 'Accounts (Section)', list each 'Days Past Due/Asset Classification' vector (one line per account)."

    ]
}