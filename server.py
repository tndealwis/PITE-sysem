import Pyro4
import sqlite3

sqlite_connection = sqlite3.connect("tax.db", check_same_thread=False)

TAX_BRACKETS = {
    0: {
        "per_dollar": 0.19,
        "base": 0,
        "min": 18201,
        "max": 45000
    },
    1: {
        "per_dollar": 0.325,
        "base": 5092,
        "min": 45001,
        "max": 120000
    },
    2: {
        "per_dollar": 0.37,
        "base": 29467,
        "min": 120001,
        "max": 180000
    },
    3: {
        "per_dollar": 0.45,
        "base": 51667,
        "min": 180001,
    }
}


@Pyro4.expose
class TaxPayers(object):
    def is_valid_tfn(self, tfn):
        cur = sqlite_connection.cursor()
        if tfn == "":
            return None

        response = cur.execute("SELECT rowid FROM Taxpayer WHERE TFN = ?",
                               (tfn,))
        result = response.fetchone()
        cur.close()

        if not result:
            return False

        return True

    def get_tax_payer_rowid(self, tfn):
        if tfn == "":
            return

        cur = sqlite_connection.cursor()

        response = cur.execute("SELECT rowid FROM Taxpayer WHERE TFN = ?",
                               (tfn,))
        result = response.fetchone()
        cur.close()

        if not result:
            return None
        return result[0]

    def get_tax_payer_payroll_records(self, tfn):
        if tfn == "":
            return None

        cur = sqlite_connection.cursor()

        taxpayer_rowid = self.get_tax_payer_rowid(tfn)

        response = cur.execute(
                "SELECT NetIncome, TaxWithHeld FROM Pay_Roll_Record WHERE TaxpayerID = ?",
                               (int(taxpayer_rowid),))
        result = response.fetchall()
        cur.close()

        if not result:
            return None

        return result

    def get_personal_id(self, tfn):
        if tfn == "":
            return None

        cur = sqlite_connection.cursor()

        response = cur.execute("SELECT PersonID FROM Taxpayer WHERE tfn = ?",
                               (tfn,))

        result = response.fetchone()
        cur.close()

        if not result:
            return None

        return result[0]


@Pyro4.expose
class TaxCalculations(object):
    def calculate_taxable_income(self, pairs):
        taxable_income = 0
        for pair in pairs:
            taxable_income = taxable_income + (pair[0] + pair[1])
        return taxable_income

    def calculate_net_income_and_tax_withheld(self, pairs):
        net_income = 0
        total_tax_withheld = 0

        for pair in pairs:
            net_income = net_income + pair[0]
            total_tax_withheld = total_tax_withheld + pair[1]

        return [net_income, total_tax_withheld]

    def calculate_tax(self, taxable_income):
        if taxable_income <= 18200:
            return

        for k, v in TAX_BRACKETS.items():
            global tax
            if taxable_income > v["min"] and taxable_income < v["max"]:
                return v["base"] + v["per_dollar"] * (
                        taxable_income - (v["min"] - 1))

    def calculate_medical_levy(self, taxable_income):
        if taxable_income < 18000:
            return
        return taxable_income * 0.02

    def calculate_medicare_levy_surplus(self, has_private_healthcare, taxable_income):
        if has_private_healthcare:
            return 0

        if taxable_income <= 90000:
            return 0

        if taxable_income <= 105000:
            return taxable_income * 0.01

        if taxable_income <= 140000:
            return taxable_income * 0.0125

        return taxable_income * 0.015

    def calculate_tax_estimate(
            self, taxable_income, net_income, tax,
            medical_levy, medicare_levy_surplus
            ):

        return (taxable_income - net_income - tax -
                medical_levy - medicare_levy_surplus)


daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()

taxPayersUri = daemon.register(TaxPayers)
ns.register("PITE.tax_payers", taxPayersUri)

taxCalculationsUri = daemon.register(TaxCalculations)
ns.register("PITE.tax_calculations", taxCalculationsUri)

daemon.requestLoop()
