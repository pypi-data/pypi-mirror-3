#
# this is a generic stub giving you complete programatic access to
# templatise transaction entries.
#
# the context is the BLTransaction object which will contain the BLEntry resulting
# from this call.  the container is the BLTransactionTemplate
#
# A BLEntry/BLSubsidiaryEntry is constituted from:
#   id   - you should NEVER change this unless you REALLY know what you are doing!
#   desc
#   path to account
#   amount
#   a reference
#
# This script should return a list (possibly empty) of BLEntry objects
#
from Products.BastionBanking.ZCurrency import ZCurrency

from Products.BastionLedger.BLEntry import BLEntry
return [ BLEntry(script.account,
               script.getId(),
               'Ledger/Accounts/%s' % script.account,
               account.salary / 52,
               script.getId()) ]
