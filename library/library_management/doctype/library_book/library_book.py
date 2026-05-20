from frappe.model.document import Document
import frappe

class LibraryBook(Document):

    def validate(self):

        self.validate_quantity()

    def validate_quantity(self):

        if self.available_quantity <= 0:

            frappe.throw(
                "Available Quantity cannot be negative"
            )