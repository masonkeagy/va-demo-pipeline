using Microsoft.Xrm.Sdk;
using Xunit;
using D365CustomerService.Plugins.Customer;

namespace D365CustomerService.Tests.Plugins
{
    public class CustomerUpdatePluginTests
    {
        [Fact]
        public void CustomerUpgradedToVip_ShouldReturnTrue()
        {
            // Arrange
            var contactEntity = new Entity("contact");
            contactEntity["customer_type"] = "VIP";

            var plugin = new CustomerUpdatePlugin();

            // Act
            var result = plugin.HandleCustomerTierChange(contactEntity);

            // Assert
            Assert.True(result);
        }

        [Fact]
        public void CustomerRemainsStandard_ShouldReturnFalse()
        {
            // Arrange
            var contactEntity = new Entity("contact");
            contactEntity["customer_type"] = "Standard";

            var plugin = new CustomerUpdatePlugin();

            // Act
            var result = plugin.HandleCustomerTierChange(contactEntity);

            // Assert
            Assert.False(result);
        }

        [Fact]
        public void MissingCustomerType_ShouldReturnFalse()
        {
            // Arrange
            var contactEntity = new Entity("contact");
            // No customer_type field set

            var plugin = new CustomerUpdatePlugin();

            // Act
            var result = plugin.HandleCustomerTierChange(contactEntity);

            // Assert
            Assert.False(result);
        }
    }
}