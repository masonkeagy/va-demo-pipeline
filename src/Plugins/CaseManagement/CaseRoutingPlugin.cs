using System;
using Microsoft.Xrm.Sdk;

namespace D365CustomerService.Plugins.CaseManagement
{
    /// <summary>
    /// CaseRoutingPlugin
    /// ------------------
    /// Fires on Create/Update of the "incident" (Case) entity.
    /// Business Rule: VIP customers automatically receive high-priority
    /// case routing so support agents triage them first.
    ///
    /// Registration (for reference):
    ///   Message: Create, Update
    ///   Primary Entity: incident
    ///   Stage: PreOperation
    /// </summary>
    public class CaseRoutingPlugin : IPlugin
    {
        public void Execute(IServiceProvider serviceProvider)
        {
            var context = (IPluginExecutionContext)
                serviceProvider.GetService(typeof(IPluginExecutionContext));

            var tracingService = (ITracingService)
                serviceProvider.GetService(typeof(ITracingService));

            if (!context.InputParameters.Contains("Target"))
            {
                tracingService.Trace("CaseRoutingPlugin: No Target found, exiting.");
                return;
            }

            var caseEntity = (Entity)context.InputParameters["Target"];

            if (caseEntity.LogicalName != "incident")
            {
                tracingService.Trace(
                    $"CaseRoutingPlugin: Target is '{caseEntity.LogicalName}', not 'incident'. Skipping.");
                return;
            }

            ApplyVipPriorityRouting(caseEntity, tracingService);
        }

        /// <summary>
        /// Applies the VIP priority business rule to a case entity.
        /// Exposed as internal-testable logic separate from Execute()
        /// so unit tests can call it directly without a full plugin context.
        /// </summary>
        public static void ApplyVipPriorityRouting(Entity caseEntity, ITracingService tracingService = null)
        {
            const string CustomerTypeField = "customer_type";
            const string PriorityField = "prioritycode";
            const string VipValue = "VIP";
            const int HighPriorityOptionSetValue = 1;

            if (caseEntity.Contains(CustomerTypeField) &&
                caseEntity[CustomerTypeField]?.ToString() == VipValue)
            {
                caseEntity[PriorityField] = new OptionSetValue(HighPriorityOptionSetValue);
                tracingService?.Trace("CaseRoutingPlugin: VIP customer detected. Priority set to High (1).");
            }
            else
            {
                tracingService?.Trace("CaseRoutingPlugin: Non-VIP customer. No priority override applied.");
            }
        }
    }
}