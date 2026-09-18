using System;
using Microsoft.Xrm.Sdk;

namespace D365CustomerService.Plugins.CaseManagement
{
    /// <summary>
    /// CaseValidationPlugin
    /// ---------------------
    /// Fires on Create of the "incident" (Case) entity.
    /// Business Rule: A case cannot be created without a subject (title)
    /// and must be associated with a valid customer record.
    ///
    /// Registration (for reference):
    ///   Message: Create
    ///   Primary Entity: incident
    ///   Stage: PreValidation
    /// </summary>
    public class CaseValidationPlugin : IPlugin
    {
        public void Execute(IServiceProvider serviceProvider)
        {
            var context = (IPluginExecutionContext)
                serviceProvider.GetService(typeof(IPluginExecutionContext));

            var tracingService = (ITracingService)
                serviceProvider.GetService(typeof(ITracingService));

            if (!context.InputParameters.Contains("Target"))
            {
                return;
            }

            var caseEntity = (Entity)context.InputParameters["Target"];

            if (caseEntity.LogicalName != "incident")
            {
                return;
            }

            ValidateCase(caseEntity, tracingService);
        }

        internal void ValidateCase(Entity caseEntity, ITracingService tracingService = null)
        {
            const string TitleField = "title";
            const string CustomerField = "customerid";

            if (!caseEntity.Contains(TitleField) ||
                string.IsNullOrWhiteSpace(caseEntity[TitleField]?.ToString()))
            {
                tracingService?.Trace("CaseValidationPlugin: Missing required field 'title'.");
                throw new InvalidPluginExecutionException(
                    "A case must have a Subject/Title before it can be created.");
            }

            if (!caseEntity.Contains(CustomerField))
            {
                tracingService?.Trace("CaseValidationPlugin: Missing required field 'customerid'.");
                throw new InvalidPluginExecutionException(
                    "A case must be associated with a valid customer.");
            }

            tracingService?.Trace("CaseValidationPlugin: Validation passed.");
        }
    }
}