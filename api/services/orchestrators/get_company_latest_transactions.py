from domain.models.Exceptions import LedgerEntryNotFoundError
from services import LedgerEntryService


def get_latest_transactions(receiver_company_id: str, limit: int = 10):
        """
        Returns a list of tuples: (LedgerEntry, detail_object)
        detail_object is either CheckTransactionDetails or CompanyTransactionDetails
        """
        # Step 1: fetch latest ledger entries via service
        entries = LedgerEntryService.query_ledger_entries(
            filters={"receiver_company_id": receiver_company_id},
            limit=limit
        )

        if not entries:
            raise LedgerEntryNotFoundError(f"No ledger entries found for company {receiver_company_id}")

        result = []
        for entry in entries:
            # Step 2: determine subtype via relationship
            if entry.check_transaction_details is not None:
                detail = entry.check_transaction_details
            elif entry.company_transaction_details is not None:
                detail = entry.company_transaction_details
            else:
                detail = None  # generic ledger entry with no extra details

            result.append((entry, detail))

        return result