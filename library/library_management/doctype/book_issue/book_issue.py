import frappe
from frappe.model.document import Document


class BookIssue(Document):

    def validate(self):

        self.validate_dates()
        self.validate_book_issue()

    def validate_dates(self):

        if self.return_date and self.issue_date:

            if self.return_date < self.issue_date:

                frappe.throw(
                    "Return Date cannot be before Issue Date"
                )

    def validate_book_issue(self):

        issued_books = []

        for row in self.books:

            # Skip Empty Rows
            if not row.book:
                continue

            # Prevent Duplicate Books in Same Issue
            if row.book in issued_books:

                frappe.throw(
                    f"Book {row.book} added multiple times in same issue"
                )

            issued_books.append(row.book)

            # Fetch Book Document
            book = frappe.get_doc(
                "Library Book",
                row.book
            )

            # Check Availability
            if book.available_quantity < 1:

                frappe.throw(
                    f"Book {book.book_title} is not available"
                )

            # Check Duplicate Submitted Issue
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