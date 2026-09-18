/**
 * ============================================
 * CustomerPriorityControl
 * ============================================
 * PCF (PowerApps Component Framework) control that visually
 * renders case priority with a badge, automatically styled
 * as "VIP" when the bound customer type is VIP.
 *
 * This mirrors the business logic in CaseRoutingPlugin.cs
 * (server-side) and caseForm.js (client-side), but renders
 * a richer custom UI component directly on the form.
 * ============================================
 */

import { IInputs, IOutputs } from "./generated/ManifestTypes";

export class CustomerPriorityControl
    implements ComponentFramework.StandardControl<IInputs, IOutputs>
{
    private container!: HTMLDivElement;
    private notifyOutputChanged!: () => void;
    private badgeElement!: HTMLDivElement;
    private currentPriorityValue: number | null = null;

    private static readonly VIP_CUSTOMER_TYPE = "VIP";
    private static readonly HIGH_PRIORITY_VALUE = 1;

    /**
     * Called once when the control is initialized.
     */
    public init(
        context: ComponentFramework.Context<IInputs>,
        notifyOutputChanged: () => void,
        state: ComponentFramework.Dictionary,
        container: HTMLDivElement
    ): void {
        this.container = container;
        this.notifyOutputChanged = notifyOutputChanged;

        this.badgeElement = document.createElement("div");
        this.badgeElement.className = "customer-priority-badge";
        this.container.appendChild(this.badgeElement);

        this.renderBadge(context);
    }

    /**
     * Called whenever any bound property value changes
     * (e.g., customerType or priorityValue updates).
     */
    public updateView(context: ComponentFramework.Context<IInputs>): void {
        this.renderBadge(context);
    }

    /**
     * Renders (or re-renders) the priority badge based on
     * current bound property values.
     */
    private renderBadge(context: ComponentFramework.Context<IInputs>): void {
        const customerType = context.parameters.customerType?.raw ?? "";
        const priorityParam = context.parameters.priorityValue;

        const isVip = customerType === CustomerPriorityControl.VIP_CUSTOMER_TYPE;

        // Auto-apply high priority for VIP customers (mirrors plugin/form logic)
        if (isVip && priorityParam?.raw !== CustomerPriorityControl.HIGH_PRIORITY_VALUE) {
            this.currentPriorityValue = CustomerPriorityControl.HIGH_PRIORITY_VALUE;
            this.notifyOutputChanged();
        } else {
            this.currentPriorityValue = priorityParam?.raw ?? null;
        }

        this.badgeElement.textContent = isVip
            ? "⭐ VIP — High Priority"
            : this.getPriorityLabel(this.currentPriorityValue);

        this.badgeElement.className = isVip
            ? "customer-priority-badge customer-priority-badge--vip"
            : "customer-priority-badge";
    }

    /**
     * Maps a raw OptionSet numeric value to a display label.
     * Placeholder mapping - adjust to match actual `prioritycode`
     * OptionSet values in the target environment.
     */
    private getPriorityLabel(value: number | null): string {
        switch (value) {
            case 1:
                return "High Priority";
            case 2:
                return "Normal Priority";
            case 3:
                return "Low Priority";
            default:
                return "Priority Not Set";
        }
    }

    /**
     * Called by the framework to get the current output values
     * when the bound property (priorityValue) has changed.
     */
    public getOutputs(): IOutputs {
        return {
            priorityValue: this.currentPriorityValue ?? undefined,
        };
    }

    /**
     * Called when the control is removed from the DOM.
     * Used for cleanup (event listeners, timers, etc.).
     */
    public destroy(): void {
        this.container.innerHTML = "";
    }
}