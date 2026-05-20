import frappe
from frappe.model.document import Document
from frappe.utils import date_diff


class BookIssue(Document):

    def validate(self):

        self.validate_dates()
        self.calculate_charges()
        self.validate_book_issue()

    def validate_dates(self):

        if self.return_date and self.issue_date:

            if self.return_date < self.issue_date:

                frappe.throw(
                    "Return Date cannot be before Issue Date"
                )

    def calculate_charges(self):

        if self.issue_date and self.return_date:

            self.total_days = date_diff(
                self.return_date,
                self.issue_date
            )

            # SAME DAY RETURN
            if self.total_days <= 0:

                self.total_days = 0

                self.total_charge = self.minimum_charge

            # NORMAL CHARGE
            else:

                self.total_charge = (
                    self.total_days * self.price_per_day
                )

    def validate_book_issue(self):

        issued_books = []

        for row in self.books:

            if not row.book:
                continue

            # Prevent Duplicate Books
            if row.book in issued_books:

                frappe.throw(
                    f"Book {row.book} added multiple times in same issue"
                )

            issued_books.append(row.book)

            # Fetch Book
            book = frappe.get_doc(
                "Library Book",
                row.book
            )

            # Check Availability
            if book.available_quantity < 1:

                frappe.throw(
                    f"Book {book.book_title} is not available"
                )

            # Duplicate Submitted Issue Check
            existing_issues = frappe.get_all(
                "Book Issue",
                filters={
                    "library_member": self.library_member,
                    "docstatus": 1
                },
                fields=["name"]
            )

            for issue in existing_issues:

                issue_doc = frappe.get_doc(
                    "Book Issue",
                    issue.name
                )

                for issued_book in issue_doc.books:

                    if issued_book.book == row.book:

                        frappe.throw(
                            f"{self.library_member} already issued book {row.book}"
                        )

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