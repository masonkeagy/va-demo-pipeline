using Microsoft.Xrm.Sdk;
using Xunit;
using D365CustomerService.Plugins.CaseManagement;

namespace D365CustomerService.Tests.Plugins
{
    public class CaseRoutingPluginTests
    {
        [Fact]
        public void PatientAdvocacyInquiry_ShouldRouteToPatientAdvocateQueue()
        {
            // Arrange
            var caseEntity = new Entity("incident");
            caseEntity["va_inquiry_source"]   = "AskVA";
            caseEntity["va_inquiry_category"] = "PatientAdvocacy";

            var plugin = new CaseRoutingPlugin();

            // Act
            plugin.RouteInquiry(caseEntity);

            // Assert
            Assert.True(caseEntity.Contains("va_routing_queue"));
            Assert.Equal("PatientAdvocate", caseEntity["va_routing_queue"].ToString());
        }

        [Fact]
        public void GeneralVHAInquiry_ShouldRouteToGeneralVHAQueue()
        {
            // Arrange
            var caseEntity = new Entity("incident");
            caseEntity["va_inquiry_source"]   = "AskVA";
            caseEntity["va_inquiry_category"] = "BenefitsQuestion";

            var plugin = new CaseRoutingPlugin();

            // Act
            plugin.RouteInquiry(caseEntity);

            // Assert
            Assert.True(caseEntity.Contains("va_routing_queue"));
            Assert.Equal("GeneralVHA", caseEntity["va_routing_queue"].ToString());
        }

        [Fact]
        public void NonAskVASource_ShouldNotApplyRouting()
        {
            // Arrange - inquiry did not come through Ask VA
            var caseEntity = new Entity("incident");
            caseEntity["va_inquiry_source"]   = "PhoneCall";
            caseEntity["va_inquiry_category"] = "PatientAdvocacy";

            var plugin = new CaseRoutingPlugin();

            // Act
            plugin.RouteInquiry(caseEntity);

            // Assert - no routing applied for non-AskVA sources
            Assert.False(caseEntity.Contains("va_routing_queue"));
        }

        [Fact]
        public void MissingInquirySource_ShouldNotApplyRouting()
        {
            // Arrange - no source field set
            var caseEntity = new Entity("incident");
            caseEntity["va_inquiry_category"] = "PatientAdvocacy";

            var plugin = new CaseRoutingPlugin();

            // Act
            plugin.RouteInquiry(caseEntity);

            // Assert
            Assert.False(caseEntity.Contains("va_routing_queue"));
        }

        [Fact]
        public void MissingCategory_ShouldDefaultToGeneralVHAQueue()
        {
            // Arrange - source is AskVA but no category set
            var caseEntity = new Entity("incident");
            caseEntity["va_inquiry_source"] = "AskVA";

            var plugin = new CaseRoutingPlugin();

            // Act
            plugin.RouteInquiry(caseEntity);

            // Assert - defaults to general queue when category unknown
            Assert.True(caseEntity.Contains("va_routing_queue"));
            Assert.Equal("GeneralVHA", caseEntity["va_routing_queue"].ToString());
        }
    }
}