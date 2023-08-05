#
# iterate thru employees applying the payment transaction ...
#
for employee in script.Accounts.objectValues():
 script.Pay_Employee([employee], date)

