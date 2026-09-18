/**
 * ============================================
 * caseForm.js
 * ============================================
 * Client-side script for the Case (incident) form.
 *
 * Business Rule: VIP customers automatically receive
 * high-priority case flagging directly on the form,
 * giving agents immediate visual feedback before save.
 *
 * Registration (for reference):
 *   Form: Case (incident) - Main Form
 *   Event: OnLoad, OnChange (customer_type field)
 * ============================================
 */

/**
 * Sets case priority to High when customer_type is VIP.
 * @param {Xrm.Events.EventContext} executionContext
 */
function setCasePriority(executionContext) {
    const formContext = executionContext.getFormContext();

    const customerTypeAttribute = formContext.getAttribute("customer_type");
    const priorityAttribute = formContext.getAttribute("prioritycode");

    if (!customerTypeAttribute || !priorityAttribute) {
        console.warn("setCasePriority: Required attributes not found on form.");
        return;
    }

    const customerType = customerTypeAttribute.getValue();

    if (customerType === "VIP") {
        priorityAttribute.setValue(1); // High priority OptionSet value
        showVipNotification(formContext);
    }
}

/**
 * Displays a form-level notification when VIP priority is auto-applied.
 * @param {Xrm.FormContext} formContext
 */
function showVipNotification(formContext) {
    formContext.ui.setFormNotification(
        "VIP customer detected — priority automatically set to High.",
        "INFO",
        "vip_priority_notification"
    );
}

/**
 * Clears the VIP notification (e.g., called on form save or field reset).
 * @param {Xrm.FormContext} formContext
 */
function clearVipNotification(formContext) {
    formContext.ui.clearFormNotification("vip_priority_notification");
}

// Export for testability (Node/Jest) while remaining compatible
// with the D365 form script runtime (which does not use modules).
if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        setCasePriority,
        showVipNotification,
        clearVipNotification,
    };
}