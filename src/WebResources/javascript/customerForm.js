/**
 * ============================================
 * customerForm.js
 * ============================================
 * Client-side script for the Customer (contact) form.
 *
 * Business Rule: When a user manually changes a customer's
 * type to VIP, prompt for confirmation since this affects
 * case routing/priority downstream.
 *
 * Registration (for reference):
 *   Form: Contact - Main Form
 *   Event: OnChange (customer_type field)
 * ============================================
 */

/**
 * Handles the customer_type field change event.
 * @param {Xrm.Events.EventContext} executionContext
 */
function onCustomerTypeChange(executionContext) {
    const formContext = executionContext.getFormContext();
    const customerTypeAttribute = formContext.getAttribute("customer_type");

    if (!customerTypeAttribute) {
        console.warn("onCustomerTypeChange: 'customer_type' attribute not found.");
        return;
    }

    const newValue = customerTypeAttribute.getValue();

    if (newValue === "VIP") {
        flagAsVipCustomer(formContext);
    }
}

/**
 * Applies UI-level changes when a customer becomes VIP
 * (e.g., highlighting the field, showing a notification).
 * @param {Xrm.FormContext} formContext
 */
function flagAsVipCustomer(formContext) {
    formContext.ui.setFormNotification(
        "This customer has been upgraded to VIP status. Open cases will be reviewed for priority.",
        "WARNING",
        "vip_customer_notification"
    );
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        onCustomerTypeChange,
        flagAsVipCustomer,
    };
}