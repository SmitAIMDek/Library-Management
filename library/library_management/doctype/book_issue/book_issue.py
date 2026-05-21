import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime


class BookIssue(Document):

    # =====================================================
    # MAIN VALIDATE
    # =====================================================

    def validate(self):

        self.validate_books()

        self.calculate_total_charges()

    # =====================================================
    # VALIDATE BOOKS
    # =====================================================

    def validate_books(self):

        unique_books = []

        for row in self.books:

            # Quantity always 1
            row.quantity = 1

            # Prevent duplicate books
            if row.book in unique_books:

                frappe.throw(
                    _("Same book cannot be added multiple times")
                )

            unique_books.append(row.book)

            # Fetch book
            book = frappe.get_doc(
                "Library Book",
                row.book
            )

            # Check stock
            if book.available_quantity <= 0:

                frappe.throw(
                    _(f"Book {row.book} is out of stock")
                )

    # =====================================================
    # CALCULATE TOTAL CHARGES
    # =====================================================

    def calculate_total_charges(self):

        total = 0

        # Convert dates
        issue_date = datetime.strptime(
            str(self.issue_date),
            "%Y-%m-%d"
        )

        return_date = datetime.strptime(
            str(self.return_date),
            "%Y-%m-%d"
        )

        # Calculate total days
        total_days = (
            return_date - issue_date
        ).days

        # Same day logic
        if total_days <= 0:
            total_days = 0

        self.total_days = total_days

        # Loop through all books
        for row in self.books:

            # Skip empty row
            if not row.book:
                continue

            # Fetch Library Book
            book = frappe.get_doc(
                "Library Book",
                row.book
            )

            # Get prices safely
            price_per_day = float(
                book.price_per_day or 0
            )

            minimum_charge = float(
                book.minimum_charge or 0
            )

            # DEBUG MESSAGE
            frappe.msgprint(
                f"""
                <b>Book:</b> {row.book}<br>
                <b>Price Per Day:</b> {price_per_day}<br>
                <b>Minimum Charge:</b> {minimum_charge}<br>
                <b>Total Days:</b> {total_days}
                """
            )

            # SAME DAY CHARGE
            if total_days == 0:

                total += minimum_charge

            # MULTIPLE DAYS CHARGE
            else:

                total += (
                    total_days *
                    price_per_day
                )

        # Final total
        self.total_charge = total

    # =====================================================
    # REDUCE STOCK ON SUBMIT
    # =====================================================

    def on_submit(self):

        for row in self.books:

            if not row.book:
                continue

            book = frappe.get_doc(
                "Library Book",
                row.book
            )

            book.available_quantity -= 1

            book.save()

    # =====================================================
    # RETURN STOCK ON CANCEL
    # =====================================================

    def on_cancel(self):

        for row in self.books:

            if not row.book:
                continue

            book = frappe.get_doc(
                "Library Book",
                row.book
            )

            book.available_quantity += 1

            book.save()