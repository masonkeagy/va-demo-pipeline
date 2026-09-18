using Microsoft.Xrm.Sdk;
using Xunit;
using D365CustomerService.Plugins.CaseManagement;

namespace D365CustomerService.Tests.Plugins
{
    public class CaseValidationPluginTests
    {
        [Fact]
        public void CaseWithTitleAndCustomer_ShouldPassValidation()
        {
            // Arrange
            var caseEntity = new Entity("incident");
            caseEntity["title"] = "Printer not working";
            caseEntity["customerid"] = new EntityReference("contact", System.Guid.NewGuid());

            var plugin = new CaseValidationPlugin();

            // Act & Assert (should not throw)
            var exception = Record.Exception(() => plugin.ValidateCase(caseEntity));
            Assert.Null(exception);
        }

        [Fact]
        public void CaseWithMissingTitle_ShouldThrowInvalidPluginExecutionException()
        {
            // Arrange
            var caseEntity = new Entity("incident");
            caseEntity["customerid"] = new EntityReference("contact", System.Guid.NewGuid());
            // No "title" field set

            var plugin = new CaseValidationPlugin();

            // Act & Assert
            var exception = Assert.Throws<InvalidPluginExecutionException>(
                () => plugin.ValidateCase(caseEntity));

            Assert.Contains("Subject/Title", exception.Message);
        }

        [Fact]
        public void CaseWithEmptyTitle_ShouldThrowInvalidPluginExecutionException()
        {
            // Arrange
            var caseEntity = new Entity("incident");
            caseEntity["title"] = "   "; // whitespace only
            caseEntity["customerid"] = new EntityReference("contact", System.Guid.NewGuid());

            var plugin = new CaseValidationPlugin();

            // Act & Assert
            Assert.Throws<InvalidPluginExecutionException>(
                () => plugin.ValidateCase(caseEntity));
        }

        [Fact]
        public void CaseWithMissingCustomer_ShouldThrowInvalidPluginExecutionException()
        {
            // Arrange
            var caseEntity = new Entity("incident");
            caseEntity["title"] = "Billing question";
            // No "customerid" field set

            var plugin = new CaseValidationPlugin();

            // Act & Assert
            var exception = Assert.Throws<InvalidPluginExecutionException>(
                () => plugin.ValidateCase(caseEntity));

            Assert.Contains("valid customer", exception.Message);
        }
    }
}