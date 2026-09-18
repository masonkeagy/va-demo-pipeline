/**
 * ============================================
 * ComponentFramework.d.ts (STUB - Global Ambient Declaration)
 * ============================================
 * IMPORTANT: This file must NOT contain any top-level
 * import/export statements. Doing so turns it into a
 * MODULE instead of a GLOBAL declaration, which breaks
 * the ComponentFramework namespace resolution.
 * ============================================
 */

declare namespace ComponentFramework {
    interface Context<TInputs> {
        parameters: TInputs;
    }

    interface Dictionary {
        [key: string]: any;
    }

    namespace PropertyTypes {
        interface OptionSetProperty {
            raw: number | null;
        }

        interface StringProperty {
            raw: string | null;
        }
    }

    interface StandardControl<TInputs, TOutputs> {
        init(
            context: Context<TInputs>,
            notifyOutputChanged: () => void,
            state: Dictionary,
            container: HTMLDivElement
        ): void;

        updateView(context: Context<TInputs>): void;

        getOutputs(): TOutputs;

        destroy(): void;
    }
}