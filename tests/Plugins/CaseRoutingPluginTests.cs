using Microsoft.Xrm.Sdk;
using Xunit;
using D365CustomerService.Plugins.CaseManagement;

namespace D365CustomerService.Tests.Plugins
{
    public class CaseRoutingPluginTests
    {
        [Fact]
        public void VipCustomer_ShouldReceiveHighPriority()
        {
            // Arrange
            var caseEntity = new Entity("incident");
            caseEntity["customer_type"] = "VIP";

            var plugin = new CaseRoutingPlugin();

            // Act
            plugin.ApplyVipPriorityRouting(caseEntity);

            // Assert
            Assert.True(caseEntity.Contains("prioritycode"));
            Assert.Equal(
                1,
                ((OptionSetValue)caseEntity["prioritycode"]).Value);
        }

        [Fact]
        public void StandardCustomer_ShouldNotReceivePriorityOverride()
        {
            // Arrange
            var caseEntity = new Entity("incident");
            caseEntity["customer_type"] = "Standard";

            var plugin = new CaseRoutingPlugin();

            // Act
            plugin.ApplyVipPriorityRouting(caseEntity);

            // Assert
            Assert.False(caseEntity.Contains("prioritycode"));
        }

        [Fact]
        public void MissingCustomerType_ShouldNotThrowAndShouldNotSetPriority()
        {
            // Arrange
            var caseEntity = new Entity("incident");
            // No customer_type field set at all

            var plugin = new CaseRoutingPlugin();

            // Act
            plugin.ApplyVipPriorityRouting(caseEntity);

            // Assert
            Assert.False(caseEntity.Contains("prioritycode"));
        }
    }
}