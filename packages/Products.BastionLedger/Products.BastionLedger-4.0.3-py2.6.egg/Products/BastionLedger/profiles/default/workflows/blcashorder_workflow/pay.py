##parameters=state_info
order = state_info.object

if not order.status() == 'invoiced':
    order.manage_invoice()

order.manage_pay()

