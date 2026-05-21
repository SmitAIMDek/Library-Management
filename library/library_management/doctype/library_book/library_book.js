// Copyright (c) 2026, smit and contributors
// For license information, please see license.txt

frappe.ui.form.on('Library Book', {

    refresh: function(frm) {

        if (frm.fields_dict.book_history_link) {

            frm.fields_dict.book_history_link.$wrapper.html(`

                <div style="margin-top:10px;">

                    <a
                        href="#"
                        id="view-book-history"
                        style="
                            font-size:14px;
                            font-weight:bold;
                            color:#2490ef;
                            text-decoration:none;
                        "
                    >
                        View Members Who Issued This Book
                    </a>

                </div>

            `);

            setTimeout(() => {

                $('#view-book-history').click(function() {

                    frappe.call({

                        method: "frappe.client.get_list",

                        args: {

                            doctype: "Book Issue",

                            fields: [
                                "name",
                                "library_member",
                                "issue_date",
                                "return_date"
                            ],

                            limit_page_length: 100

                        },

                        callback: function(r) {

                            let message = "";

                            if (r.message) {

                                let promises = [];

                                r.message.forEach(issue => {

                                    promises.push(

                                        frappe.call({

                                            method: "frappe.client.get",

                                            args: {
                                                doctype: "Book Issue",
                                                name: issue.name
                                            }

                                        }).then(res => {

                                            let found = false;

                                            res.message.books.forEach(row => {

                                                if (row.book === frm.doc.name) {
                                                    found = true;
                                                }

                                            });

                                            if (found) {

                                                message += `

                                                    <div style="
                                                        margin-bottom:15px;
                                                        padding:10px;
                                                        border-bottom:1px solid #ddd;
                                                    ">

                                                        <b>Member:</b>
                                                        ${issue.library_member}

                                                        <br>

                                                        <b>Book Issue:</b>
                                                        ${issue.name}

                                                        <br>

                                                        <b>Issue Date:</b>
                                                        ${issue.issue_date}

                                                        <br>

                                                        <b>Return Date:</b>
                                                        ${issue.return_date}

                                                    </div>

                                                `;
                                            }

                                        })

                                    );

                                });

                                Promise.all(promises).then(() => {

                                    if (!message) {

                                        message = `
                                            <b>
                                                No member has issued this book yet.
                                            </b>
                                        `;
                                    }

                                    frappe.msgprint({

                                        title: __('Book Issue History'),

                                        message: message,

                                        indicator: 'blue'

                                    });

                                });

                            }

                        }

                    });

                });

            }, 300);

        }

    }

});
