using System;
using Microsoft.Xrm.Sdk;

namespace D365CustomerService.Plugins.CaseManagement
{
    /// <summary>
    /// AskVAInquiryRoutingPlugin
    /// --------------------------
    /// Fires on Create of the "incident" (Case) entity.
    ///
    /// Business Rule: Ask VA inquiries submitted by or on behalf of
    /// a Veteran are routed to the Patient Advocate queue when the
    /// inquiry category is patient advocacy related, keeping them
    /// separate from general VHA queues.
    ///
    /// Registration:
    ///   Message:        Create
    ///   Primary Entity: incident
    ///   Stage:          PreOperation
    /// </summary>
    public class CaseRoutingPlugin : IPlugin
    {
        // Queue routing constants
        private const string InquiryCategoryField  = "va_inquiry_category";
        private const string QueueField            = "va_routing_queue";
        private const string SourceField           = "va_inquiry_source";

        private const string PatientAdvocacyCategory = "PatientAdvocacy";
        private const string PatientAdvocateQueue    = "PatientAdvocate";
        private const string GeneralVHAQueue         = "GeneralVHA";
        private const string AskVASource             = "AskVA";

        public void Execute(IServiceProvider serviceProvider)
        {
            var context = (IPluginExecutionContext)
                serviceProvider.GetService(typeof(IPluginExecutionContext));

            var tracingService = (ITracingService)
                serviceProvider.GetService(typeof(ITracingService));

            if (!context.InputParameters.Contains("Target"))
            {
                tracingService?.Trace("AskVAInquiryRoutingPlugin: No Target found, exiting.");
                return;
            }

            var caseEntity = (Entity)context.InputParameters["Target"];

            if (caseEntity.LogicalName != "incident")
            {
                tracingService?.Trace(
                    $"AskVAInquiryRoutingPlugin: Target is '{caseEntity.LogicalName}', not 'incident'. Skipping.");
                return;
            }

            RouteInquiry(caseEntity, tracingService);
        }

        /// <summary>
        /// Routes an Ask VA inquiry to the appropriate queue based on
        /// inquiry category. Patient advocacy cases are separated from
        /// general VHA queues to ensure proper handling.
        ///
        /// Exposed as public for direct unit testing without a full
        /// plugin execution context.
        /// </summary>
        public void RouteInquiry(Entity caseEntity, ITracingService tracingService = null)
        {
            // Only route inquiries that came through Ask VA
            if (!caseEntity.Contains(SourceField) ||
                caseEntity[SourceField]?.ToString() != AskVASource)
            {
                tracingService?.Trace(
                    "AskVAInquiryRoutingPlugin: Inquiry source is not AskVA. No routing applied.");
                return;
            }

            // Route patient advocacy cases to dedicated queue
            if (caseEntity.Contains(InquiryCategoryField) &&
                caseEntity[InquiryCategoryField]?.ToString() == PatientAdvocacyCategory)
            {
                caseEntity[QueueField] = PatientAdvocateQueue;
                tracingService?.Trace(
                    "AskVAInquiryRoutingPlugin: Patient advocacy inquiry routed to Patient Advocate queue.");
            }
            else
            {
                caseEntity[QueueField] = GeneralVHAQueue;
                tracingService?.Trace(
                    "AskVAInquiryRoutingPlugin: Inquiry routed to General VHA queue.");
            }
        }
    }
}