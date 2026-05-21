import frappe

from frappe.model.document import Document

from datetime import datetime


class BookIssue(Document):

    # =========================================
    # VALIDATE
    # =========================================

    def validate(self):

        self.calculate_total_charges()

    # =========================================
    # CALCULATE TOTAL CHARGES
    # =========================================

    def calculate_total_charges(self):

        total = 0

        # =========================================
        # DATE CONVERSION
        # =========================================

        issue_date = datetime.strptime(
            str(self.issue_date),
            "%Y-%m-%d"
        )

        return_date = datetime.strptime(
            str(self.return_date),
            "%Y-%m-%d"
        )

        # =========================================
        # RENTAL DAYS
        # =========================================

        rental_days = (
            return_date - issue_date
        ).days

        # SAME DAY CHECK
        is_same_day = (
            str(self.issue_date) ==
            str(self.return_date)
        )

        # If not same day,
        # minimum 1 rental day
        if rental_days <= 0:
            rental_days = 1

        # =========================================
        # RESET VALUES
        # =========================================

        self.late_days = 0
        self.fine_amount = 0

        # =========================================
        # BOOK CHARGES
        # =========================================

        total_books = 0

        for row in self.books:

            if not row.book:
                continue

            total_books += 1

            # FETCH BOOK
            book = frappe.get_doc(
                "Library Book",
                row.book
            )

            price_per_day = float(
                book.price_per_day or 0
            )

            minimum_charge = float(
                book.minimum_charge or 0
            )

            # =========================================
            # SAME DAY CHARGE
            # =========================================

            if is_same_day:

                total += minimum_charge

            # =========================================
            # PER DAY CHARGE
            # =========================================

            else:

                total += (
                    rental_days *
                    price_per_day
                )

        # =========================================
        # LATE FINE
        # =========================================

        if self.actual_return_date:

            actual_return_date = datetime.strptime(
                str(self.actual_return_date),
                "%Y-%m-%d"
            )

            late_days = (
                actual_return_date - return_date
            ).days

            if late_days > 0:

                self.late_days = late_days

                self.fine_amount = (

                    late_days *

                    float(self.fine_per_day or 0) *

                    total_books

                )

                total += self.fine_amount

        # =========================================
        # TOTAL DAYS
        # =========================================

        self.total_days = (
            rental_days +
            self.late_days
        )

        # =========================================
        # FINAL TOTAL
        # =========================================

        self.total_charge = total