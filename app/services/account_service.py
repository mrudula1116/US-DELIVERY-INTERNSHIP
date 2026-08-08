from pathlib import Path
import json
from typing import List, Dict, Optional

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

ACCOUNTS_FILE = BASE_DIR / "Data" / "accounts.json"


# ---------------------------------------------------------
# Load Accounts
# ---------------------------------------------------------

def load_accounts() -> List[Dict]:
    """
    Load customer accounts from Data/accounts.json.

    Supports:
    1. A JSON list of account objects
    2. A JSON dictionary containing account objects
    3. A dictionary containing an 'accounts' list
    """

    if not ACCOUNTS_FILE.exists():
        raise FileNotFoundError(
            f"Accounts file not found: {ACCOUNTS_FILE}"
        )

    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    # -----------------------------------------------------
    # Format 1:
    # [
    #   {"account_id": "ACC-3847", ...}
    # ]
    # -----------------------------------------------------

    if isinstance(data, list):
        return data

    # -----------------------------------------------------
    # Format 2:
    # {
    #   "accounts": [
    #       {"account_id": "ACC-3847", ...}
    #   ]
    # }
    # -----------------------------------------------------

    if isinstance(data, dict) and "accounts" in data:
        accounts = data["accounts"]

        if isinstance(accounts, list):
            return accounts

    # -----------------------------------------------------
    # Format 3:
    # {
    #   "ACC-3847": {
    #       "company": "Initech",
    #       ...
    #   }
    # }
    # -----------------------------------------------------

    if isinstance(data, dict):

        accounts = []

        for key, value in data.items():

            if isinstance(value, dict):

                account = value.copy()

                # Add account_id if it is stored as the key
                if "account_id" not in account:
                    account["account_id"] = key

                accounts.append(account)

        if accounts:
            return accounts

    # -----------------------------------------------------
    # Unknown format
    # -----------------------------------------------------

    raise ValueError(
        f"Unsupported accounts.json format: {type(data).__name__}"
    )


# ---------------------------------------------------------
# Find Account
# ---------------------------------------------------------

def get_account(account_id: str) -> Optional[Dict]:
    """
    Find an account by account_id.
    """

    account_id = account_id.strip()

    accounts = load_accounts()

    for account in accounts:

        if str(account.get("account_id", "")).strip() == account_id:
            return account

    return None


# ---------------------------------------------------------
# Update Account
# ---------------------------------------------------------

def save_accounts(accounts: List[Dict]) -> None:
    """
    Save accounts back to Data/accounts.json.
    """

    with open(
        ACCOUNTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            accounts,
            file,
            indent=2
        )


# ---------------------------------------------------------
# Top-up Account
# ---------------------------------------------------------

def topup_account(account_id: str, amount: float) -> dict:
    """
    Add USD credit to an existing customer account.
    """

    if amount <= 0:
        raise ValueError("Top-up amount must be greater than 0")

    accounts = load_accounts()

    for account in accounts:

        if account.get("account_id") == account_id:

            # The API expects balance_usd.
            # Existing company data does not contain this field,
            # so initialize it to zero for the first top-up.
            if "balance_usd" not in account:
                account["balance_usd"] = 0.0

            account["balance_usd"] += amount

            ACCOUNTS_FILE.write_text(
                json.dumps(accounts, indent=2),
                encoding="utf-8"
            )

            return account

    raise ValueError(
        f"Account {account_id} not found"
    )