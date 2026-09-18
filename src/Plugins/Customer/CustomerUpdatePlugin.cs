using System;
using Microsoft.Xrm.Sdk;

namespace D365CustomerService.Plugins.Customer
{
    /// <summary>
    /// CustomerUpdatePlugin
    /// ---------------------
    /// Fires on Update of the "contact" (Customer) entity.
    /// Business Rule: When a customer's tier is upgraded to VIP,
    /// automatically flag all their open cases for priority review.
    ///
    /// Registration (for reference):
    ///   Message: Update
    ///   Primary Entity: contact
    ///   Stage: PostOperation
    ///   Filtering Attributes: customer_type
    /// </summary>
    public class CustomerUpdatePlugin : IPlugin
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

            var contactEntity = (Entity)context.InputParameters["Target"];

            if (contactEntity.LogicalName != "contact")
            {
                return;
            }

            HandleCustomerTierChange(contactEntity, tracingService);
        }

        public static bool HandleCustomerTierChange(Entity contactEntity, ITracingService tracingService = null)
        {
            const string CustomerTypeField = "customer_type";
            const string VipValue = "VIP";

            if (contactEntity.Contains(CustomerTypeField) &&
                contactEntity[CustomerTypeField]?.ToString() == VipValue)
            {
                tracingService?.Trace(
                    "CustomerUpdatePlugin: Customer upgraded to VIP. Open cases should be flagged for review.");
                // In a real implementation, this would query related "incident" records
                // via IOrganizationService and update their priority.
                return true;
            }

            return false;
        }
    }
}