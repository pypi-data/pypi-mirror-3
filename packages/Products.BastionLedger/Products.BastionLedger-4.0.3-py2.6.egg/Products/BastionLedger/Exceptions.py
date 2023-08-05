#
#    Copyright (C) 2007-2009  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

class LedgerError(Exception):
    """
    Any BastionLedger Exception
    """

class PostingError(LedgerError):
    """
    A general error in transaction/account entry posting
    """

class AlreadyPostedError(PostingError):
    """
    raised when an attempt to post something more than once
    this throws the entry in question
    """
    pass

class UnpostedError(PostingError):
    """
    raised when we expected to see an entry posted, but it in fact hasn't been
    this throws the entry in question
    """
    pass

class OrphanEntryError(PostingError):
    """
    raised when an entry is found for which no transaction exists
    """
    pass

class IncorrectAmountError(PostingError):
    """
    raised when an entry is found to not have the amount suggested in the transaction
    """
    pass

class FXAmountError(PostingError):
    """
    raised when there is no historical FX rate and/or the amount does not compute
    """
    pass

class UnbalancedError(PostingError):
    """
    raised when the debit side doesn't equal the credit side
    """

class InvalidTransition(LedgerError):
    """
    raised when a workflow action is not valid based on the internal state of the object
    """
    pass

class InvalidState(LedgerError):
    """
    raised when a workflow action attempts to transit the object to an invalid internal state
    """
    pass

class UnexpectedTransaction(LedgerError):
    """
    raised when a transaction that we materialised doesn't appear to match what we expected
    """
    pass

class MissingAssociation(LedgerError):
    """
    raised when the link to an account is not found
    """
    pass

class InvalidPeriodError(LedgerError):
    """
    raised when date-mismatch for end of period processing
    """
    pass

class DepreciationError(LedgerError):
    """
    raised to indicate exception with depreciation/amortisation
    """
    pass

class ProcessError(LedgerError):
    """
    raised when an error has occurred running a ledger process
    """
