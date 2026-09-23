/**
 * ============================================
 * caseForm.test.js
 * ============================================
 * Jest unit tests for caseForm.js
 * Mocks the Xrm.FormContext API since these tests
 * run outside an actual D365 form runtime.
 * ============================================
 */

const { setCasePriority, clearVipNotification } = require("../../src/WebResources/javascript/caseForm");

/**
 * Helper to build a mock Xrm executionContext with
 * configurable attribute values.
 */
function createMockExecutionContext({
    customerType = null,
    includeCustomerType = true,
    includePriority = true,
} = {}) {
    const attributes = {
        ...(includeCustomerType && {
            customer_type: {
                getValue: jest.fn(() => customerType),
            },
        }),
        ...(includePriority && {
            prioritycode: {
                setValue: jest.fn(),
            },
        }),
    };

    const formContext = {
        getAttribute: jest.fn((name) => attributes[name]),
        ui: {
            setFormNotification: jest.fn(),
            clearFormNotification: jest.fn(),
        },
    };

    return {
        getFormContext: () => formContext,
        _attributes: attributes, // exposed for assertions
        _formContext: formContext,
    };
}

describe("caseForm.js", () => {
    describe("setCasePriority", () => {
        test("VIP customer should have priority set to High (1)", () => {
            const executionContext = createMockExecutionContext({ customerType: "VIP" });

            setCasePriority(executionContext);

            expect(executionContext._attributes.prioritycode.setValue).toHaveBeenCalledWith(1);
        });

        test("VIP customer should trigger a form notification", () => {
            const executionContext = createMockExecutionContext({ customerType: "VIP" });

            setCasePriority(executionContext);

            expect(executionContext._formContext.ui.setFormNotification).toHaveBeenCalledWith(
                expect.stringContaining("VIP customer detected"),
                "INFO",
                "vip_priority_notification"
            );
        });

        test("Non-VIP customer should NOT have priority overridden", () => {
            const executionContext = createMockExecutionContext({ customerType: "Standard" });

            setCasePriority(executionContext);

            expect(executionContext._attributes.prioritycode.setValue).not.toHaveBeenCalled();
        });

        test("Missing customer_type attribute should not throw", () => {
            const executionContext = createMockExecutionContext({ includeCustomerType: false });

            expect(() => setCasePriority(executionContext)).not.toThrow();
        });
    });

    describe("clearVipNotification", () => {
        test("should call clearFormNotification with correct key", () => {
            const executionContext = createMockExecutionContext({});
            const formContext = executionContext._formContext;

            clearVipNotification(formContext);

            expect(formContext.ui.clearFormNotification).toHaveBeenCalledWith("vip_priority_notification");
        });
    });
});