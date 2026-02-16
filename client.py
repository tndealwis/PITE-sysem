import Pyro4
import tkinter as tk


tfn = ""
net_income_tax_withheld_pairs = []
has_private_healthcare = False
taxable_income = 0
net_income = 0
total_tax_withheld = 0
tax = 0
medical_levy = 0
medicare_levy_surplus = 0
tax_estimate = 0
personal_id = 0

tax_calculations = Pyro4.Proxy("PYRONAME:PITE.tax_calculations")
tax_records = Pyro4.Proxy("PYRONAME:PITE.tax_payers")

window = tk.Tk()
window.title("PITE")


def request_calculations():
    global taxable_income
    global net_income
    global total_tax_withheld
    global tax
    global medical_levy
    global medicare_levy_surplus
    global tax_estimate

    taxable_income = tax_calculations.calculate_taxable_income(
            net_income_tax_withheld_pairs)
    net_income_tax_withheld_totals = tax_calculations.calculate_net_income_and_tax_withheld(
            net_income_tax_withheld_pairs)
    net_income = net_income_tax_withheld_totals[0]
    total_tax_withheld = net_income_tax_withheld_totals[1]
    tax = tax_calculations.calculate_tax(taxable_income)
    medical_levy = tax_calculations.calculate_medical_levy(taxable_income)
    medicare_levy_surplus = tax_calculations.calculate_medicare_levy_surplus(
            has_private_healthcare, taxable_income)
    tax_estimate = tax_calculations.calculate_tax_estimate(
            taxable_income, net_income, tax,
            medical_levy, medicare_levy_surplus
            )


def load_results_page(f_window):
    frame = tk.Frame(f_window)

    tfn_text = "No TFN" if len(tfn) == 0 else f"TFN {tfn}"
    tax_estimate_text = f"Refundable Tax Amount ${tax_estimate}" if tax_estimate > 0 else f"Payable Tax Amount ${-tax_estimate}"

    tk.Label(frame, text=f"Personal ID: {personal_id}").grid(row=0, pady=10)
    tk.Label(frame, text=tfn_text).grid(row=1, pady=10)
    tk.Label(frame, text=f"Taxable Income ${taxable_income}").grid(row=3, pady=10)
    tk.Label(frame, text=f"Tax Withheld ${total_tax_withheld}").grid(row=4, pady=10)
    tk.Label(frame, text=f"Net Income ${net_income}").grid(row=5, pady=10)
    tk.Label(frame, text=tax_estimate_text).grid(row=6, pady=10)

    return frame


def load_private_healthcare_page(f_window):
    frame = tk.Frame(f_window)

    tk.Label(frame, text="Do you have private Healthcare?").grid(
            row=0, padx=10, pady=10)

    options = [
            "Yes",
            "No"
    ]

    selected = tk.StringVar()
    selected.set("No")

    dropDown = tk.OptionMenu(frame, selected, *options)
    dropDown.grid(row=1, padx=10, pady=10)

    def on_next():
        global has_private_healthcare
        if selected.get() == "Yes":
            has_private_healthcare = True
        request_calculations()
        frame.destroy()
        load_results_page(f_window).pack()

    nextButton = tk.Button(frame, text="Next", fg="black", command=on_next)
    nextButton.grid(row=2, padx=10, pady=10)

    return frame


def net_income_tax_withheld_pairs_table(frame):
    table_frame = tk.Frame(frame)
    table_frame.grid(row=0)

    row = 0
    for pair in net_income_tax_withheld_pairs:
        title = tk.Entry(table_frame, disabledforeground="black")
        title.insert(
                0, f"Bi-weekly {row + 1}")
        title.grid(row=row, column=0)
        title.configure(state="disabled")
        taxable_income = tk.Entry(table_frame, disabledforeground="black")
        taxable_income.insert(
                0, pair[0])
        taxable_income.grid(row=row, column=1)
        taxable_income.config(state="disabled")
        tax_withheld = tk.Entry(table_frame, disabledforeground="black")
        tax_withheld.insert(
                0, pair[1])
        tax_withheld.grid(row=row, column=2)
        tax_withheld.config(state="disabled")
        row = row + 1


def load_net_income_tax_withheld_page(f_window):
    global bi_week_counter
    bi_week_counter = 1
    bi_week_max = 26
    error = ""

    frame = tk.Frame(f_window)
    table_frame = tk.Frame(frame)

    error_message_frame = tk.Frame(frame)

    error_message = tk.Label(error_message_frame, text=error, bg="red", fg="white")
    error_message.grid(row=0, padx=10, pady=10)

    net_income_frame = tk.Frame(frame)
    net_income_frame.grid(row=1, padx=10, pady=10)
    net_income_label = tk.Label(
            net_income_frame,
            text=f"Enter Net Income for bi-week {bi_week_counter}"
    )
    net_income_label.grid(row=0, padx=10)
    net_income_entry = tk.Entry(net_income_frame)
    net_income_entry.grid(row=0, column=1, padx=10)

    tax_withheld_frame = tk.Frame(frame)
    tax_withheld_frame.grid(row=2, padx=10, pady=10)
    tax_withheld_label = tk.Label(
            tax_withheld_frame,
            text=f"Enter tax withheld for bi-week {bi_week_counter}"
    )
    tax_withheld_label.grid(row=0, padx=10)
    tax_withheld_entry = tk.Entry(tax_withheld_frame)
    tax_withheld_entry.grid(row=0, column=1, padx=10)

    def on_pair_add():
        global error
        global bi_week_counter
        bi_week_counter = bi_week_counter + 1

        try:
            net_income_tax_withheld_pairs.append([
                int(net_income_entry.get()),
                int(tax_withheld_entry.get())
            ])
        except ValueError:
            error = "Input not a number"
            error_message_frame.grid(row=0, padx=10, pady=10)
            error_message.config(text=error)
            return

        if bi_week_counter > bi_week_max:
            return

        net_income_label.config(
                text=f"Enter Net Income for bi-week {bi_week_counter}")
        tax_withheld_label.config(
                text=f"Enter tax withheld for bi-week {bi_week_counter}")
        net_income_entry.delete(0, 'end')
        tax_withheld_entry.delete(0, 'end')

        for widget in table_frame.winfo_children():
            widget.destroy()

        net_income_tax_withheld_pairs_table(table_frame)

    pair_add_button = tk.Button(frame, text="Add", fg="black",
                                command=on_pair_add)
    pair_add_button.grid(row=3, padx=10, pady=10)

    def on_submit():
        frame.destroy()
        load_private_healthcare_page(f_window).pack()

    pairs_submit_button = tk.Button(frame, text="Submit",
                                    fg="black", command=on_submit)
    pairs_submit_button.grid(row=4, padx=10, pady=10)

    table_frame.grid(row=5, padx=10, pady=10)

    return frame


def load_personal_id_page(f_window):
    frame = tk.Frame(f_window)

    tk.Label(frame, text="Enter Personal ID").grid(row=0, pady=10)
    personal_id_entry = tk.Entry(frame)
    personal_id_entry.grid(row=0, column=1, pady=10)

    def on_personal_id_submit():
        global personal_id
        if len(personal_id_entry.get()) > 6 or len(personal_id_entry.get()) < 6:
            return

        try:
            personal_id = int(personal_id_entry.get())
            frame.destroy()
            load_net_income_tax_withheld_page(f_window).pack()
        except ValueError:
            return

    personal_id_submit_button = tk.Button(
            frame, text="Submit", fg="black", command=on_personal_id_submit)
    personal_id_submit_button.grid(row=1, pady=10)

    return frame


def load_tfn_submit_page(f_window):
    frame = tk.Frame(f_window)

    error = ""
    error_frame = tk.Frame(frame)
    error_label = tk.Label(error_frame, text=error, fg="white", bg="red")
    error_label.grid(row=0, padx=10, pady=10)

    tfn_input_frame = tk.Frame(frame)
    tfn_input_frame.grid(row=1, padx=10, pady=10)

    tk.Label(tfn_input_frame, text="Enter TFN").grid(row=0, padx=10)

    tfn_entry = tk.Entry(tfn_input_frame)
    tfn_entry.grid(row=0, column=1, padx=10)

    def on_submit_tfn():
        global net_income_tax_withheld_pairs
        global error
        global tfn
        global personal_id

        tfn = tfn_entry.get()

        if (tax_records.is_valid_tfn(tfn)):
            net_income_tax_withheld_pairs = tax_records.get_tax_payer_payroll_records(
                    tfn)
            personal_id = tax_records.get_personal_id(tfn)
            frame.destroy()
            load_private_healthcare_page(f_window).pack()
            return

        error = "Please enter valid TFN"
        error_frame.grid(row=0, padx=10, pady=10)
        error_label.config(text=error)

    submit_tfn = tk.Button(
            frame, text="Submit TFN", fg="black", command=on_submit_tfn)
    submit_tfn.grid(row=2, padx=10, pady=10)

    def on_no_tfn():
        frame.destroy()
        load_personal_id_page(f_window).pack()

    no_tfn = tk.Button(
            frame, text="I don't have a TFN", fg="red", command=on_no_tfn)
    no_tfn.grid(row=3, padx=10, pady=10)

    return frame


tfn_submit_frame = load_tfn_submit_page(window)
tfn_submit_frame.pack()

window.mainloop()
